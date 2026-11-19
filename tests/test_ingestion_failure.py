
from unittest.mock import patch

import chromadb

from app.config import CHROMA_PATH, COLLECTION_NAME
from app.ingestion import ingest_documents


def test_embedding_failure_preserves_old_document():

    filename = "employee_benefits.txt"

    client = chromadb.PersistentClient(path=CHROMA_PATH)
    collection = client.get_collection(name=COLLECTION_NAME)

    document_path = __import__("pathlib").Path(
        "data/documents"
    ) / filename

    original_content = document_path.read_text(encoding="utf-8")

    before = collection.get(
        where={"source": filename},
        include=["documents", "metadatas"]
    )

    assert before["ids"], "No existing chunks found."

    old_ids = set(before["ids"])
    old_documents = dict(zip(before["ids"], before["documents"]))

    try:
        # Change the document so ingestion cannot skip it.
        document_path.write_text(
            original_content + "\nTemporary failure-test content.",
            encoding="utf-8"
        )

        with patch(
            "app.ingestion.generate_embedding",
            side_effect=RuntimeError("Simulated embedding failure")
        ) as mock_embedding:

            try:
                ingest_documents()
                raise AssertionError("Expected embedding failure did not occur.")
            except RuntimeError as error:
                assert str(error) == "Simulated embedding failure"

            # Confirm the mocked embedding function was actually called.
            assert mock_embedding.called, "Embedding failure was not triggered."

    finally:
        # Always restore the original local document.
        document_path.write_text(
            original_content,
            encoding="utf-8"
        )

    after = collection.get(
        where={"source": filename},
        include=["documents", "metadatas"]
    )

    new_ids = set(after["ids"])
    new_documents = dict(zip(after["ids"], after["documents"]))

    assert old_ids == new_ids, "Existing chunk IDs were changed."
    assert old_documents == new_documents, "Existing document content was lost."

    print("\nPASS: Embedding failure was triggered.")
    print("PASS: Previous indexed document was preserved.")


if __name__ == "__main__":
    test_embedding_failure_preserves_old_document()
