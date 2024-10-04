import os
from dotenv import load_dotenv
load_dotenv()

from langchain_openai import ChatOpenAI
from langchain_openai import OpenAIEmbeddings
from langchain_community.graphs import Neo4jGraph
from langchain_community.vectorstores import Neo4jVector
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains import create_retrieval_chain
from langchain_core.prompts import ChatPromptTemplate

llm = ChatOpenAI(
    openai_api_key=os.getenv('OPENAI_API_KEY'), 
    temperature=0
)

embedding_provider = OpenAIEmbeddings(
    openai_api_key=os.getenv('OPENAI_API_KEY')
    )

graph = Neo4jGraph(
    url=os.getenv('NEO4J_URI'),
    username=os.getenv('NEO4J_USERNAME'),
    password=os.getenv('NEO4J_PASSWORD')
)

chunk_vector = Neo4jVector.from_existing_index(
    embedding_provider,
    graph=graph,
    index_name="vector",
    embedding_node_property="embedding",
    text_node_property="text",
    retrieval_query="""
// get the document
MATCH (node)-[:PART_OF]->(d:Document)
WITH node, score, d
// get the entities
MATCH (node)-[:HAS_ENTITY]-(e)
WITH node, score, d, collect(e) as nodeslist
// find the relationships between the entities related to the document
MATCH p = (e)-[r]-(e2)
WHERE e in nodeslist and e2 in nodeslist
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

instructions = (
    "Use the given context to answer the question."
    "Reply with an answer that includes the id of the document and other relevant information from the text."
    "If you don't know the answer, say you don't know."
    "Context: {context}"
)

prompt = ChatPromptTemplate.from_messages(
    [
        ("system", instructions),
        ("human", "{input}"),
    ]
)

chunk_retriever = chunk_vector.as_retriever()
chunk_chain = create_stuff_documents_chain(llm, prompt)
chunk_retriever = create_retrieval_chain(
    chunk_retriever, 
    chunk_chain
)

def find_chunk(q):
    return chunk_retriever.invoke({"input": q})

while True:
    q = input(">")
    print(find_chunk(q))
