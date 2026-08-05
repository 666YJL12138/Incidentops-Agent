import json
from pathlib import Path

from rag.retrieve import search_knowledge


EVAL_PATH = Path("data/eval_queries.json")


def is_hit(results: list[dict], expected_source: str, k: int) -> bool:
    top_results = results[:k]

    return any(
        expected_source in result["source"]
        for result in top_results
    )


def main():
    items = json.loads(
        EVAL_PATH.read_text(encoding="utf-8")
    )

    hit_1 = 0
    hit_3 = 0
    hit_5 = 0

    for item in items:
        results = search_knowledge(
            query=item["query"],
            top_k=5,
        )

        hit_1 += int(
            is_hit(results, item["expected_source"], 1)
        )
        hit_3 += int(
            is_hit(results, item["expected_source"], 3)
        )
        hit_5 += int(
            is_hit(results, item["expected_source"], 5)
        )

        top_source = (
            results[0]["source"]
            if results
            else "no result"
        )

        print(
            f'query={item["query"]}\n'
            f'expected={item["expected_source"]}\n'
            f'top1={top_source}\n'
        )

    total = len(items)

    print("=== Retrieval Evaluation ===")
    print(f"Queries: {total}")
    print(f"Hit@1: {hit_1 / total:.2%}")
    print(f"Hit@3: {hit_3 / total:.2%}")
    print(f"Hit@5: {hit_5 / total:.2%}")


if __name__ == "__main__":
    main()
