from langchain_openai import OpenAIEmbeddings
from langchain_community.graphs import Neo4jGraph
from langchain_community.vectorstores import Neo4jVector

embedding_provider = OpenAIEmbeddings(
    openai_api_key="sk-...",
    model="text-embedding-ada-002"
    )

graph = Neo4jGraph(
    url="bolt://localhost:7687",
    username="neo4j",
    password="pleaseletmein"
)

for chunk in chunks:

    # Embed the chunk
    chunk_embedding = embedding_provider.embed_query(chunk.page_content)

    # Add the Document and Chunk nodes to the graph
    properties = {
        "filename": chunk.metadata["source"],
        "text": chunk.page_content,
        # Create the embedding for the chunk
        "embedding": chunk_embedding
    }
    
    graph.query("""
        MERGE (d:Document {fileName: $filename})
        MERGE (c:Chunk {fileName: $filename})
        SET c.text = $text
        CALL db.create.setNodeVectorProperty(c, 'embedding', $embedding)
        MERGE (d)<-[:PART_OF]-(c)
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


