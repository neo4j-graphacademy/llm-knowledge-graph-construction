import os

from langchain_community.document_loaders import DirectoryLoader, PyPDFLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_neo4j import Neo4jGraph
from langchain_openai import ChatOpenAI
from langchain_experimental.graph_transformers import LLMGraphTransformer
from langchain_community.graphs.graph_document import Node, Relationship

from dotenv import load_dotenv
load_dotenv()

DOCS_PATH = "llm-knowledge-graph/data/marine/pdfs_ocr" # OCR yapılmış PDF dosyalarının bulunduğu dizin
# Bu dizindeki PDF dosyaları, metin parçalarına ayrılacak ve Neo4j grafiğine eklenecek.

llm = ChatOpenAI(
    openai_api_key=os.getenv('OPENAI_API_KEY'), 
    model_name="gpt-3.5-turbo"
)

embedding_provider = OpenAIEmbeddings( # metinleri vektöre dönüştürmek için kullanılır
    openai_api_key=os.getenv('OPENAI_API_KEY'),
    model="text-embedding-ada-002"
    )

graph = Neo4jGraph( # Neo4j veritabanına bağlanmak için kullanılır
    url=os.getenv('NEO4J_URI'),
    username=os.getenv('NEO4J_USERNAME'),
    password=os.getenv('NEO4J_PASSWORD')
)

doc_transformer = LLMGraphTransformer( # LLMGraphTransformer, metinleri grafik belgelerine dönüştürmek için kullanılır
    llm=llm,
    )

# Load and split the documents
loader = DirectoryLoader(DOCS_PATH, glob="**/*.pdf", loader_cls=PyPDFLoader) # belirtilen dizindeki PDF dosyalarını yükler

text_splitter = CharacterTextSplitter( # metinleri parçalara ayırmak için kullanılır
    separator="\n\n",
    chunk_size=1500, # her parçanın maksimum boyutu
    chunk_overlap=200, # parçalar arasındaki maksimum örtüşme
)

docs = loader.load()
chunks = text_splitter.split_documents(docs) # metinleri parçalara ayırır

for chunk in chunks: # her bir parça için işlem yapar

    filename = os.path.basename(chunk.metadata["source"]) # dosya adını alır
    chunk_id = f"{filename}.{chunk.metadata['page']}" # parça kimliğini oluşturur. pdf adı ve sayfa numarı ile bir benzersiz kimlik oluşturur
    print("Processing -", chunk_id) # console'a yazarak kontrol ederiz.

    # Embed the chunk
    chunk_embedding = embedding_provider.embed_query(chunk.page_content) # Metin, 1536 boyutlu embedding vektörüne dönüştürülür

    # Add the Document and Chunk nodes to the graph
    properties = {
        "filename": filename,
        "chunk_id": chunk_id,
        "text": chunk.page_content,
        "embedding": chunk_embedding
    }
    
    graph.query("""
        MERGE (d:Document {id: $filename})
        MERGE (c:Chunk {id: $chunk_id})
        SET c.text = $text
        MERGE (d)<-[:PART_OF]-(c)
        WITH c
        CALL db.create.setNodeVectorProperty(c, 'textEmbedding', $embedding)
        """, 
        properties
    )

    # Generate the entities and relationships from the chunk
    graph_docs = doc_transformer.convert_to_graph_documents([chunk]) # LLM, chunk içeriğinden kavram (entity) ve ilişkiler (relationship) çıkarır.



    # Map the entities in the graph documents to the chunk node
    # Her çıkarılan kavram node, o chunk’a HAS_ENTITY ilişkisiyle bağlanır.
    # Bu, chunk içeriğindeki kavramların grafik üzerinde nasıl temsil edileceğini belirler.
    # Her bir graph_doc için, chunk_id ile ilişkilendirilmiş bir Chunk node oluşturulur.
    for graph_doc in graph_docs:
        chunk_node = Node(
            id=chunk_id,
            type="Chunk"
        )

        for node in graph_doc.nodes: 

            graph_doc.relationships.append(
                Relationship(
                    source=chunk_node,
                    target=node, 
                    type="HAS_ENTITY"
                    )
                )

    # add the graph documents to the graph
    graph.add_graph_documents(graph_docs) # Tüm çıkarılmış kavramlar ve ilişkiler Neo4j’ye yazılır.

# Create the vector index
# Chunk düğümlerindeki textEmbedding özelliği için cosine benzerliğine dayalı bir vektör arama indeksi oluşturuluyor.
graph.query("""
    CREATE VECTOR INDEX `chunkVector`
    IF NOT EXISTS
    FOR (c: Chunk) ON (c.textEmbedding)
    OPTIONS {indexConfig: {
    `vector.dimensions`: 1536,
    `vector.similarity_function`: 'cosine'
    }};""")
