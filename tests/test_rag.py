from rag.retrieve import search_knowledge


def test_payment_timeout_retrieval():
    results = search_knowledge(
        query="payment provider timeout",
        top_k=3,
    )

    assert results

    sources = [
        result["source"]
        for result in results
    ]

    assert any(
        "payment-provider-timeout.md" in source
        or "payment-timeout.md" in source
        for source in sources
    )


def test_database_pool_retrieval():
    results = search_knowledge(
        query="database connection pool exhausted",
        top_k=3,
    )

    assert results

    sources = [
        result["source"]
        for result in results
    ]

    assert any(
        "database-connection-pool.md" in source
        or "database-pool-exhausted.md" in source
        for source in sources
    )


def test_unknown_query_returns_list():
    results = search_knowledge(
        query="unknown impossible incident",
        top_k=3,
    )

    assert isinstance(results, list)
