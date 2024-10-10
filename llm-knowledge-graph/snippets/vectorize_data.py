from langchain_openai import OpenAIEmbeddings
from langchain_community.graphs import Neo4jGraph

embedding_provider = OpenAIEmbeddings(
    openai_api_key=os.getenv('OPENAI_API_KEY'),
    model="text-embedding-ada-002"
    )

graph = Neo4jGraph(
    url=os.getenv('NEO4J_URI'),
    username=os.getenv('NEO4J_USERNAME'),
    password=os.getenv('NEO4J_PASSWORD')
)

for chunk in chunks:

    # Extract the filename
    filename = os.path.basename(chunk.metadata["source"])

    # Create a unique identifier for the chunk    
    chunk_id = f"{filename}.{chunk.metadata["page"]}"

    # Embed the chunk
    chunk_embedding = embedding_provider.embed_query(chunk.page_content)

    # Add the Document and Chunk nodes to the graph
    properties = {
        "filename": filename,
        "chunk_id": chunk_id,
        "text": chunk.page_content,
        "textEmbedding": chunk_embedding
    }

    graph.query("""
        MERGE (d:Document {id: $filename})
        MERGE (c:Chunk {id: $chunk_id})
        SET c.text = $text
        MERGE (d)<-[:PART_OF]-(c)
        WITH c
        CALL db.create.setNodeVectorProperty(c, 'textEmbedding', $embedding)
        """, 
        properties
    )

# Create the vector index
graph.query("""
    CREATE VECTOR INDEX `vector`
    FOR (c: Chunk) ON (c.embedding)
    OPTIONS {indexConfig: {
    `vector.dimensions`: 1536,
    `vector.similarity_function`: 'cosine'
    }};""")


