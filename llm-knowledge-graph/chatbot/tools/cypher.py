import os
from dotenv import load_dotenv
load_dotenv()

from llm import llm
from graph import graph

from langchain_neo4j import GraphCypherQAChain
from langchain.prompts import PromptTemplate

# You task is to update this tool to generate and run a Cypher statement, and return the results.
    
# Create cypher_generation prompt
# CYPHER_GENERATION_TEMPLATE = ""

# Create the cypher_chain
# cypher_chain = GraphCypherQAChain.from_llm

def run_cypher(q):
    # Invoke the cypher_chain
    # return  cypher_chain.invoke({"query": q})
    
    # Currently this functions returns nothing.
    return {}
  