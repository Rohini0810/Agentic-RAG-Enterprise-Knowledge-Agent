#BM25 is a keyword-based ranking algorithm. It considers:
#- How often a query term appears in a document.
#- How important that term is across the document collection.
#- Document length, so longer documents aren't automatically favored.


import re
import chromadb

from rank_bm25 import BM25Okapi

from app.config import CHROMA_PATH, COLLECTION_NAME
from app.ingestion import generate_embedding


def tokenize(text: str) -> list[str]:
    """Convert text into lowercase searchable tokens."""
    return re.findall(r"[a-zA-Z0-9_-]+", text.lower())


def reciprocal_rank_fusion(
    rankings: list[list[str]],
    k: int = 60
) -> dict[str, float]:
    """Combine multiple ranked lists using Reciprocal Rank Fusion."""

    scores = {}

    for ranking in rankings:
        for rank, document_id in enumerate(ranking, start=1):
            scores[document_id] = (
                scores.get(document_id, 0)
                + 1 / (k + rank)
            )

    return scores


def hybrid_search(query: str, top_k: int = 3):

    # Connect to ChromaDB
    client = chromadb.PersistentClient(path=CHROMA_PATH)
    collection = client.get_collection(name=COLLECTION_NAME)

    # Retrieve all stored chunks for the BM25 index
    stored = collection.get(
        include=["documents", "metadatas"]
    )

    documents = stored["documents"]
    metadatas = stored["metadatas"]
    ids = stored["ids"]

    if not documents:
        return []

    # Build the BM25 keyword search index : We convert each document into tokens and build a keyword search index.
    tokenized_documents = [
        tokenize(document) for document in documents
    ]

    bm25 = BM25Okapi(tokenized_documents)

    # 1. Dense retrieval: vector search - This searches by semantic similarity, just like our existing retrieval module.
    query_embedding = generate_embedding(query)

    dense_results = collection.query(
        query_embeddings=[query_embedding],
        n_results=min(top_k, len(documents))
    )

    dense_ranking = dense_results["ids"][0]

    # 2. Sparse retrieval: BM25 keyword search
    tokenized_query = tokenize(query)
    bm25_scores = bm25.get_scores(tokenized_query)

    sparse_indices = sorted(
        range(len(bm25_scores)),
        key=lambda i: bm25_scores[i],
        reverse=True
    )[:top_k]

    sparse_ranking = [ids[i] for i in sparse_indices]

    # 3. Combine rankings using RRF
    fused_scores = reciprocal_rank_fusion(
        [dense_ranking, sparse_ranking]
    )

    # Sort by combined relevance score
    ranked_ids = sorted(
        fused_scores,
        key=fused_scores.get,
        reverse=True
    )[:top_k]

    # Build the final results
    document_lookup = {
        document_id: {
            "document": documents[i],
            "metadata": metadatas[i]
        }
        for i, document_id in enumerate(ids)
    }

    return [
        {
            "id": document_id,
            "document": document_lookup[document_id]["document"],
            "metadata": document_lookup[document_id]["metadata"],
            "rrf_score": fused_scores[document_id]
        }
        for document_id in ranked_ids
    ]


if __name__ == "__main__":

    question = "How many annual paid leave days do employees receive?"

    results = hybrid_search(question)

    for result in results:
        print("\nDocument:", result["document"])
        print("Source:", result["metadata"]["source"])
        print("RRF Score:", result["rrf_score"])
