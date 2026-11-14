#only for vector retrieval
import chromadb

from app.config import CHROMA_PATH, COLLECTION_NAME
from app.ingestion import generate_embedding


def retrieve_documents(query: str, top_k: int = 3):

    # Connect to the existing vector database
    client = chromadb.PersistentClient(path=CHROMA_PATH)

    collection = client.get_collection(name=COLLECTION_NAME)

    # Convert the user's question into an embedding
    query_embedding = generate_embedding(query)

    # Search for the most relevant chunks
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k
    )

    return results


if __name__ == "__main__":

    question = "How many annual leave days do employees receive?"

    results = retrieve_documents(question)

    for document, metadata, distance in zip(
        results["documents"][0],
        results["metadatas"][0],
        results["distances"][0]
    ):
        print("\nRetrieved document:", document)
        print("Source:", metadata["source"])
        print("Distance:", distance)