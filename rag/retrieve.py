import json
import re
from pathlib import Path


INDEX_PATH = Path("data/knowledge_index.json")


def tokenize(text: str) -> list[str]:
    return re.findall(r"[a-zA-Z0-9_-]+", text.lower())


def load_index() -> list[dict]:
    if not INDEX_PATH.exists():
        return []

    return json.loads(INDEX_PATH.read_text(encoding="utf-8"))


def score_document(query_tokens: list[str], document: dict) -> int:
    content = document["content"].lower()
    title = document["title"].lower()

    score = 0

    for token in query_tokens:
        if token in title:
            score += 3

        if token in content:
            score += 1

    return score


def search_knowledge(query: str, top_k: int = 5) -> list[dict]:
    documents = load_index()
    query_tokens = tokenize(query)

    scored_results = []

    for document in documents:
        score = score_document(query_tokens, document)

        if score > 0:
            scored_results.append(
                {
                    "title": document["title"],
                    "source": document["source"],
                    "doc_type": document["doc_type"],
                    "score": score,
                    "preview": document["content"][:300],
                }
            )

    scored_results.sort(key=lambda item: item["score"], reverse=True)

    return scored_results[:top_k]
    