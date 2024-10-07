import os
from dotenv import load_dotenv
load_dotenv()

from llm import llm, embeddings
from graph import graph

# You task is to update this tool to query the Neo4j vector to return the most relevant documents

# Create the chunk_vector
# chunk_vector = Neo4jVector.from_existing_index

# Create the instructions and prompt
# instructions = ""
# prompt = ChatPromptTemplate.from_messages

# Create the chunk_retriever and chain
# chunk_retriever = chunk_vector.as_retriever()
# chunk_chain = create_stuff_documents_chain(llm, prompt)
# chunk_retriever = create_retrieval_chain    chunk_retriever, 

def find_chunk(q):
    # Invoke the chunk retriever
    # return chunk_retriever.invoke({"input": input})

    # Currently this functions returns nothing
    return {
        "input": q,
        "context": []
    }
