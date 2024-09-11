import os

from langchain_community.document_loaders import DirectoryLoader, PyPDFLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.graphs import Neo4jGraph
from langchain_openai import ChatOpenAI
from langchain_experimental.graph_transformers import LLMGraphTransformer
from langchain_community.graphs.graph_document import Node, Relationship

from dotenv import load_dotenv
load_dotenv()

DOCS_PATH = "llm-knowledge-graph/data/course/pdfs"

llm = ChatOpenAI(
    openai_api_key=os.getenv('OPENAI_API_KEY'), 
    model_name="gpt-3.5-turbo"
)

embedding_provider = OpenAIEmbeddings(
    openai_api_key=os.getenv('OPENAI_API_KEY'),
    model="text-embedding-ada-002"
    )

graph = Neo4jGraph(
    url=os.getenv('NEO4J_URI'),
    username=os.getenv('NEO4J_USERNAME'),
    password=os.getenv('NEO4J_PASSWORD')
)

loader = DirectoryLoader(DOCS_PATH, glob="**/*.pdf", loader_cls=PyPDFLoader)

text_splitter = CharacterTextSplitter(
    separator="\n\n",
    chunk_size=1500,
    chunk_overlap=200,
)

# tag::allowed_nodes[]
doc_transformer = LLMGraphTransformer(
    llm=llm,
    allowed_nodes=["Technology", "Concept", "Skill", "Event", "Person", "Object"],
    )
# tag::allowed_nodes[]

# tag::allowed_relationships[]
doc_transformer = LLMGraphTransformer(
    llm=llm,
    allowed_nodes=["Technology", "Concept", "Skill", "Event", "Person", "Object"],
    allowed_relationships=["USES", "HAS", "IS", "AT", "KNOWS"],
    )
# tag::allowed_relationships[]

# tag::node_properties[]
doc_transformer = LLMGraphTransformer(
    llm=llm,
    allowed_nodes=["Technology", "Concept", "Skill", "Event", "Person", "Object"],
    node_properties=["name", "description"],
    )
# end::node_properties[]

docs = loader.load()
chunks = text_splitter.split_documents(docs)

for chunk in chunks:

    chunk_id = f"{chunk.metadata["source"]}.{chunk.metadata["page"]}"
    print("Processing -", chunk_id)

    # Embed the chunk
    chunk_embedding = embedding_provider.embed_query(chunk.page_content)

    # Add the Document and Chunk nodes to the graph
    properties = {
        "filename": chunk.metadata["source"],
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
        CALL db.create.setNodeVectorProperty(c, 'embedding', $embedding)
        """, 
        properties
    )

    # Generate the graph docs
    graph_docs = doc_transformer.convert_to_graph_documents([chunk])

    # Map the entities in the graph documents to the chunk node
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
    graph.add_graph_documents([graph_doc])

    exit()

# Create the vector index
graph.query("""
    CREATE VECTOR INDEX `vector`
    IF NOT EXISTS
    FOR (c: Chunk) ON (c.embedding)
    OPTIONS {indexConfig: {
    `vector.dimensions`: 1536,
    `vector.similarity_function`: 'cosine'
    }};""")
