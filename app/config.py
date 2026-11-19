
import os

# Ollama endpoint.
# Local development uses localhost.
# Docker will override this with host.docker.internal.
OLLAMA_BASE_URL = os.getenv(
    "OLLAMA_BASE_URL",
    "http://localhost:11434"
)

LLM_MODEL = os.getenv(
    "LLM_MODEL",
    "qwen2.5:3b"
)

EMBEDDING_MODEL = os.getenv(
    "EMBEDDING_MODEL",
    "nomic-embed-text"
)

DOCUMENTS_PATH = os.getenv(
    "DOCUMENTS_PATH",
    "data/documents"
)

CHROMA_PATH = os.getenv(
    "CHROMA_PATH",
    "data/chroma_db"
)

COLLECTION_NAME = os.getenv(
    "COLLECTION_NAME",
    "enterprise_knowledge"
)
