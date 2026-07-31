import json
from pathlib import Path


KNOWLEDGE_DIRS = [
    Path("data/runbooks"),
    Path("data/postmortems"),
]

INDEX_PATH = Path("data/knowledge_index.json")


def read_markdown_files():
    documents = []

    for knowledge_dir in KNOWLEDGE_DIRS:
        for path in knowledge_dir.glob("*.md"):
            text = path.read_text(encoding="utf-8")
            title = extract_title(text, path)

            documents.append(
                {
                    "title": title,
                    "source": str(path),
                    "content": text,
                    "doc_type": knowledge_dir.name,
                }
            )

    return documents


def extract_title(text: str, path: Path) -> str:
    for line in text.splitlines():
        if line.startswith("# "):
            return line.replace("# ", "").strip()

    return path.stem.replace("-", " ").title()


def build_index():
    documents = read_markdown_files()

    INDEX_PATH.write_text(
        json.dumps(documents, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    print(f"Indexed {len(documents)} documents into {INDEX_PATH}")


if __name__ == "__main__":
    build_index()
    