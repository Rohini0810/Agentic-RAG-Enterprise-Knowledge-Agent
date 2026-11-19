
from pathlib import Path
import hashlib

import chromadb
import requests

from app.chunking import chunk_text
from app.config import (
    OLLAMA_BASE_URL,
    EMBEDDING_MODEL,
    DOCUMENTS_PATH,
    CHROMA_PATH,
    COLLECTION_NAME,
)


def generate_embedding(text: str) -> list[float]:
    """Generate an embedding using the configured Ollama model."""

    response = requests.post(
        f"{OLLAMA_BASE_URL}/api/embed",
        json={
            "model": EMBEDDING_MODEL,
            "input": text,
        },
        timeout=60,
    )

    response.raise_for_status()

    return response.json()["embeddings"][0]


def load_documents() -> list[dict]:
    """Load all TXT documents from the configured directory."""

    documents = []
    folder = Path(DOCUMENTS_PATH)

    if not folder.exists():
        raise FileNotFoundError(
            f"Documents directory does not exist: {folder}"
        )

    for file_path in sorted(folder.glob("*.txt")):
        content = file_path.read_text(encoding="utf-8")

        documents.append({
            "filename": file_path.name,
            "content": content,
        })

    return documents


def calculate_content_hash(content: str) -> str:
    """Calculate a SHA-256 hash to detect document changes."""

    return hashlib.sha256(
        content.encode("utf-8")
    ).hexdigest()


def get_existing_sources(collection) -> dict:
    """Return existing source names and their stored content hashes."""

    result = collection.get(include=["metadatas"])

    sources = {}

    for metadata in result["metadatas"] or []:
        source = metadata.get("source")

        if source:
            sources[source] = metadata.get("content_hash")

    return sources


def ingest_documents() -> dict:
    """
    Synchronize local TXT documents with ChromaDB.

    - New documents are indexed.
    - Modified documents are re-indexed.
    - Unchanged documents are skipped.
    - Deleted documents are removed.
    - Existing chunks are retained if embedding generation fails.
    """

    client = chromadb.PersistentClient(
        path=CHROMA_PATH
    )

    collection = client.get_or_create_collection(
        name=COLLECTION_NAME
    )

    documents = load_documents()

    existing_sources = get_existing_sources(collection)

    current_sources = {
        document["filename"]
        for document in documents
    }

    added = 0
    modified = 0
    unchanged = 0
    deleted = 0

    # Process new and modified documents.
    for document in documents:

        filename = document["filename"]
        content = document["content"]

        content_hash = calculate_content_hash(content)

        # Skip documents whose content has not changed.
        if (
            filename in existing_sources
            and existing_sources[filename] == content_hash
        ):
            unchanged += 1
            print(f"Unchanged: {filename}")
            continue

        chunks = chunk_text(content)

        # Remove exact duplicate chunks while preserving order.
        chunks = list(dict.fromkeys(chunks))

        # Generate every embedding BEFORE deleting old chunks.
        # If embedding generation fails, the old index remains intact.
        embeddings = [
            generate_embedding(chunk)
            for chunk in chunks
        ]

        ids = [
            f"{filename}_{index}"
            for index in range(len(chunks))
        ]

        metadatas = [
            {
                "source": filename,
                "chunk_index": index,
                "content_hash": content_hash,
            }
            for index in range(len(chunks))
        ]

        # Replace the old document only after all embeddings succeed.
        collection.delete(
            where={"source": filename}
        )

        if chunks:
            collection.upsert(
                ids=ids,
                documents=chunks,
                embeddings=embeddings,
                metadatas=metadatas,
            )

        if filename in existing_sources:
            modified += 1
            print(f"Updated: {filename}")
        else:
            added += 1
            print(f"Added: {filename}")

    # Remove documents that no longer exist locally.
    deleted_sources = (
        set(existing_sources.keys()) - current_sources
    )

    for filename in deleted_sources:
        collection.delete(
            where={"source": filename}
        )

        deleted += 1
        print(f"Deleted: {filename}")

    summary = {
        "added": added,
        "modified": modified,
        "unchanged": unchanged,
        "deleted": deleted,
        "total_chunks": collection.count(),
    }

    print("\nDocument synchronization completed.")
    print(f"Added: {added}")
    print(f"Modified: {modified}")
    print(f"Unchanged: {unchanged}")
    print(f"Deleted: {deleted}")
    print(f"Total chunks: {collection.count()}")

    return summary


if __name__ == "__main__":
    ingest_documents()
