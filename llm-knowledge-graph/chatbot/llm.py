import os
from dotenv import load_dotenv
load_dotenv()

# tag::llm[]
# Create the LLM
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(
    openai_api_key=os.getenv('OPENAI_API_KEY'),
    model_name="gpt-4o-mini"
)
# end::llm[]

# tag::embedding[]
# Create the Embedding model
from langchain_openai import OpenAIEmbeddings

embeddings = OpenAIEmbeddings(
    openai_api_key=os.getenv('OPENAI_API_KEY')
)
# end::embedding[]
