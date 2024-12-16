import os
from dotenv import load_dotenv
load_dotenv()

from llm import llm
from graph import graph

from langchain_neo4j import GraphCypherQAChain
from langchain.prompts import PromptTemplate

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

The question is:
{question}"""

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
RETURN e.id

# Find documents that reference entities
MATCH (d:Document)<-[:PART_OF]-(c:Chunk)-[:HAS_ENTITY]->(e)
WHERE e.id =~ '(?i)entityName'
RETURN d.id, c.id, c.text, e.id

The question is:
{question}"""

cypher_generation_prompt = PromptTemplate(
    template=CYPHER_GENERATION_TEMPLATE,
    input_variables=["schema", "question"],
)

cypher_chain = GraphCypherQAChain.from_llm(
    llm,
    graph=graph,
    cypher_prompt=cypher_generation_prompt,
    verbose=True,
    allow_dangerous_requests=True
)

def run_cypher(q):
    cypher_chain.invoke({"query": q})
    

  