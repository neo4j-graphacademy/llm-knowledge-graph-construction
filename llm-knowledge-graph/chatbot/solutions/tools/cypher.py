
# Bu dosya, LangChain kullanarak LLM destekli Cypher sorguları üretmek için kullanılan bir araçtır. Kullanıcıdan gelen sorulara göre, Neo4j veritabanında sorgular oluşturur ve çalıştırır.

import os
from dotenv import load_dotenv
load_dotenv()

from llm import llm
from graph import graph

from langchain_neo4j import GraphCypherQAChain
from langchain.prompts import PromptTemplate




# Şablonun güncellenmiş hali. Şablon değiştirlebilir.
CYPHER_GENERATION_TEMPLATE = """Task:Generate Cypher statement to query a graph database.
Instructions:
Use only the provided relationship types and properties in the schema.
Do not use any other relationship types or properties that are not provided.
Only include the generated Cypher statement in your response.

Always use case insensitive search when matching strings.

Schema:
{schema}

The question is:
{question}"""

# PromptTemplate: Kullanıcı sorusu ve şema bilgisi ile bir Cypher sorgusu üretmek için kullanılan şablon nesnesi
cypher_generation_prompt = PromptTemplate(
    template=CYPHER_GENERATION_TEMPLATE, # Cypher sorgusu oluşturmak için kullanılan şablon
    input_variables=["schema", "question"],# şablonun alacağı değişkenler
)

# LangChain'in GraphCypherQAChain yapısı ile LLM destekli Cypher üretimi zinciri oluşturuluyor
cypher_chain = GraphCypherQAChain.from_llm(
    llm,
    graph=graph,
    cypher_prompt=cypher_generation_prompt,
    verbose=True, # Zincir işlemleri terminale detaylı şekilde loglanır
    allow_dangerous_requests=True # Güvenli olmayan Cypher komutlarının da çalıştırılmasına izin ver (DİKKATLİ OLMALIYIZ)
)

# Dışarıdan gelen kullanıcı sorusunu alıp LLM destekli zincire geçirir ve Cypher sorgusunu çalıştırır
def run_cypher(q):
    return cypher_chain.invoke({"query": q})
      