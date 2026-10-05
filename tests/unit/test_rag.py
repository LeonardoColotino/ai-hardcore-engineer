from app.tools.rag_search import RAGSearchTool


def test_retriever_returns_sources(rag_retriever):
    r = rag_retriever.retrieve("Can I use a Getnet payment link on WhatsApp?")
    assert r.hits
    assert r.sources[0].url


def test_rag_tool_returns_predictable_shape(rag_retriever):
    result = RAGSearchTool(rag_retriever).run("Getnet Pix")
    assert result.success
    assert isinstance(result.data["contexts"], list)
    assert result.metadata["retrieved_documents"] >= 1


def test_rag_blank_query_fails(rag_retriever):
    assert not RAGSearchTool(rag_retriever).run("  ").success
