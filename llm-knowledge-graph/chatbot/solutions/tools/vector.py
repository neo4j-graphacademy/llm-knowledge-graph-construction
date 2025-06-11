
# Bu kod, Neo4j üzerinde saklanan metin parçalarını (chunks) ve onların bilgi grafiği ilişkilerini vektör indeksinden çekerek,  llm'e  veriyor. 

# .env dosyasındaki ortam değişkenlerini yüklüyoruz (örneğin API anahtarları, veritabanı bilgileri).
import os
from dotenv import load_dotenv
load_dotenv()

# OpenAI'nin Chat modeli ve gömülü vektör (embedding) oluşturucu sınıfı içe aktarılıyor.
from langchain_openai import ChatOpenAI
from langchain_openai import OpenAIEmbeddings

# Neo4j veritabanı ile hem grafik sorguları hem de vektör aramaları yapmak için gerekli sınıflar.
from langchain_neo4j import Neo4jGraph, Neo4jVector

# LangChain'de dökümanları birleştirmek (stuff = hepsini tek metin olarak sunmak) için kullanılan zincir.
from langchain.chains.combine_documents import create_stuff_documents_chain

# Döküman alma ve yanıt oluşturma zinciri (retrieval-augmented generation chain).
from langchain.chains.retrieval import create_retrieval_chain

# Prompt şablonu tanımlamak için kullanılır.
from langchain_core.prompts import ChatPromptTemplate

# OpenAI Chat LLM örneği oluşturuluyor. Sıcaklık 0 olduğu için yanıtlar deterministik ve tutarlı olacak.
llm = ChatOpenAI(
    openai_api_key=os.getenv('OPENAI_API_KEY'), 
    temperature=0
)

# OpenAI'nin gömülü vektör (embedding) sağlayıcısı tanımlanıyor.
embedding_provider = OpenAIEmbeddings(
    openai_api_key=os.getenv('OPENAI_API_KEY')
)

# Neo4j veritabanına bağlanmak için gerekli bağlantı bilgileri.
graph = Neo4jGraph(
    url=os.getenv('NEO4J_URI'),
    username=os.getenv('NEO4J_USERNAME'),
    password=os.getenv('NEO4J_PASSWORD')
)

# Neo4j'de önceden oluşturulmuş bir vektör indeksini kullanarak bir `Neo4jVector` nesnesi oluşturuluyor.
# Bu nesne, sorguya göre en alakalı bilgi parçacıklarını (chunks) getirmek için kullanılır.
chunk_vector = Neo4jVector.from_existing_index(
    embedding_provider,
    graph=graph,
    index_name="chunkVector",  # Neo4j'deki vektör indeksinin adı
    embedding_node_property="textEmbedding",  # Her düğümdeki embedding vektörünün bulunduğu alan
    text_node_property="text",  # Metnin bulunduğu alan
    retrieval_query="""
// Bilgi parçacığı ve onunla ilişkili bilgi grafiği verilerini getiren Cypher sorgusu
// get the document
MATCH (node)-[:PART_OF]->(d:Document)
WITH node, score, d

// get the entities and relationships for the document
MATCH (node)-[:HAS_ENTITY]->(e)
MATCH p = (e)-[r]-(e2)
WHERE (node)-[:HAS_ENTITY]->(e2)

// unwind the path, create a string of the entities and relationships
UNWIND relationships(p) as rels
WITH 
    node, 
    score, 
    d, 
    collect(apoc.text.join(
        [labels(startNode(rels))[0], startNode(rels).id, type(rels), labels(endNode(rels))[0], endNode(rels).id]
        ," ")) as kg
RETURN
    node.text as text, score,
    { 
        document: d.id,
        entities: kg
    } AS metadata
"""
)

# LLM’e verilecek sistem talimatları (system prompt).
# Modelden bağlamı kullanarak soruya cevap vermesi isteniyor.
instructions = (
    "You are a maritime expert. Answer the question based on the following texts. "
    "Make sure to include the document ID and key details from the text in your response. "
    "If the answer is not in the context, say you don't know. "
    "Context: {context}"
)

# Prompt şablonu: Modelin önce sistem talimatlarını, ardından insan girdisini almasını sağlar.
prompt = ChatPromptTemplate.from_messages(
    [
        ("system", instructions),
        ("human", "{input}"),
    ]
)

# Vektör indeksinden bilgi parçacıklarını almak için bir `retriever` tanımlanıyor.
chunk_retrieverr = chunk_vector.as_retriever()

# LLM’in gelen bilgi parçacıklarını kullanarak bir metin üretmesini sağlayan zincir.
chunk_chain = create_stuff_documents_chain(llm, prompt)

# Vektör tabanlı arama zinciri ile LLM zinciri birleştirilerek nihai sorgulama zinciri oluşturuluyor.
chunk_retriever = create_retrieval_chain(
    chunk_retrieverr, 
    chunk_chain
)

# Kullanıcıdan gelen soruyu alır, zincire gönderir ve sonucu döndürür.
def find_chunk(q):
    return chunk_retriever.invoke({"input": q})