
from pathlib import Path
import chromadb
import requests
from app.chunking import chunk_text

from app.config import (
    OLLAMA_BASE_URL,
    EMBEDDING_MODEL,
    DOCUMENTS_PATH,
    CHROMA_PATH,
    COLLECTION_NAME
)


def generate_embedding(text: str):

    response = requests.post(
        f"{OLLAMA_BASE_URL}/api/embed",
        json={
            "model": EMBEDDING_MODEL,
            "input": text
        },
        timeout=60
    )

    response.raise_for_status()

    return response.json()["embeddings"][0]


def load_documents():

    documents = []

    folder = Path(DOCUMENTS_PATH)

    for file_path in folder.glob("*.txt"):

        content = file_path.read_text(encoding="utf-8")

        documents.append({
            "filename": file_path.name,
            "content": content
        })

    return documents


#def chunk_text(text: str, chunk_size=100, overlap=20):

    words = text.split()

    chunks = []

    start = 0

    while start < len(words):

        end = start + chunk_size

        chunk = " ".join(words[start:end])

        chunks.append(chunk)

        start += chunk_size - overlap

    return chunks


def ingest_documents():

    client = chromadb.PersistentClient(
        path=CHROMA_PATH
    )

    collection = client.get_or_create_collection(
        name=COLLECTION_NAME
    )

    documents = load_documents()

    for document in documents:
        # Remove previously indexed chunks for this source - This removes all previously indexed chunks belonging to that file before re-ingesting it.
        collection.delete(
            where={"source": document["filename"]}
        )
        
        # Generate chunks
        chunks = chunk_text(document["content"])

        #Remove exact duplicate chunks while preserving order
        chunks = list(dict.fromkeys(chunks))
        
        for index, chunk in enumerate(chunks):

            embedding = generate_embedding(chunk)

            collection.upsert(
                ids=[f"{document['filename']}_{index}"],
                documents=[chunk],
                embeddings=[embedding],
                metadatas=[{
                    "source": document["filename"],
                    "chunk_index": index
                }]
            )

    print(f"Successfully ingested {len(documents)} documents.")

    print(f"Total chunks stored: {collection.count()}")


if __name__ == "__main__":

    ingest_documents()
