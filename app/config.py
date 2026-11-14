#Configuration centralizes model names, API endpoints and storage paths. If we change the model later, we won't need to edit multiple files.
OLLAMA_BASE_URL = "http://localhost:11434"

LLM_MODEL = "qwen2.5:3b"

EMBEDDING_MODEL = "nomic-embed-text"

DOCUMENTS_PATH = "data/documents"

CHROMA_PATH = "data/chroma_db"

COLLECTION_NAME = "enterprise_knowledge"
