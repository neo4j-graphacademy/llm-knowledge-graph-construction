def test_create_kg_allowed(test_helpers, monkeypatch):
    import os
    from langchain_neo4j import Neo4jGraph

    test_helpers.run_module(
        monkeypatch,
        "create_kg_allowed",
    )

    graph = Neo4jGraph(
        url=os.getenv("NEO4J_URI"),
        username=os.getenv("NEO4J_USERNAME"),
        password=os.getenv("NEO4J_PASSWORD")
        )

    result = test_helpers.run_cypher(
        graph,
        "RETURN EXISTS ((:Document)<-[:PART_OF]-(:Chunk)-[:HAS_ENTITY]->()) as exists"
        )
    
    assert result[0]["exists"]

def test_retriever(test_helpers, monkeypatch):
    
    output = test_helpers.run_module(
        monkeypatch,
        "retriever",
        ["What is hallucination?", "exit"]
    )

    assert "llm-fundamentals_1-introduction_2-hallucination.pdf" in output

def test_query_kg(test_helpers, monkeypatch):
    
    output = test_helpers.run_module(
        monkeypatch,
        "query_kg_llms",
        ["Find document ids that reference llms", "exit"]
    )

    assert "llm-fundamentals_1-introduction_1-neo4j-and-genai.pdf" in output

