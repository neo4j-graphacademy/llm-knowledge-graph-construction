import os
from langchain_openai import ChatOpenAI
from langchain_neo4j import GraphCypherQAChain, Neo4jGraph
from langchain.prompts import PromptTemplate

from dotenv import load_dotenv
load_dotenv()

# tag::llms[]
qa_llm = ChatOpenAI(
    openai_api_key=os.getenv('OPENAI_API_KEY'), 
    model="gpt-3.5-turbo",
)

cypher_llm = ChatOpenAI(
    openai_api_key=os.getenv('OPENAI_API_KEY'), 
    model="gpt-4",
    temperature=0
)
# end::llms[]

graph = Neo4jGraph(
    url=os.getenv('NEO4J_URI'),
    username=os.getenv('NEO4J_USERNAME'),
    password=os.getenv('NEO4J_PASSWORD')
)

CYPHER_GENERATION_TEMPLATE = """Task:Generate Cypher statement to query a graph database.
Instructions:
Use only the provided relationship types and properties in the schema.
Do not use any other relationship types or properties that are not provided.
Only include the generated Cypher statement in your response.

Always use case insensitive search when matching strings.

Schema:
{schema}

Examples: 
# Use case insensitive matching for entity ids
MATCH (c:Chunk)-[:HAS_ENTITY]->(e)
WHERE e.id =~ '(?i)entityName'

# Find documents that reference entities
MATCH (d:Document)<-[:PART_OF]-(:Chunk)-[:HAS_ENTITY]->(e)
WHERE e.id =~ '(?i)entityName'
RETURN d

The question is:
{question}"""

cypher_generation_prompt = PromptTemplate(
    template=CYPHER_GENERATION_TEMPLATE,
    input_variables=["schema", "question"],
)

# tag::cypher_chain[]
cypher_chain = GraphCypherQAChain.from_llm(
    qa_llm=qa_llm,
    cypher_llm=cypher_llm,
    graph=graph,
    cypher_prompt=cypher_generation_prompt,
    verbose=True,
    allow_dangerous_requests=True
)
# end::cypher_chain[]

def run_cypher(q):
    return cypher_chain.invoke({"query": q})

while True:
    q = input("> ")
    print(run_cypher(q))
