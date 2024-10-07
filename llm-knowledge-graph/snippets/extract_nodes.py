from langchain_openai import ChatOpenAI
from langchain_experimental.graph_transformers import LLMGraphTransformer

llm = ChatOpenAI(
    openai_api_key=os.getenv('OPENAI_API_KEY'), 
    model_name="gpt-3.5-turbo"
)

doc_transformer = LLMGraphTransformer(
    llm=llm,
    )

for chunk in chunks:
    # Generate the entities and relationships from the chunk
    graph_docs = doc_transformer.convert_to_graph_documents([chunk])
