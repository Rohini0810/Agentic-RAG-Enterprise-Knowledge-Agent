# System Architecture

## Goals and boundaries

The application separates ingestion, retrieval, generation, user interface, API, and observability. Ingestion prepares the knowledge base; query-time retrieval searches it. Retrieval finds evidence; generation writes an answer from that evidence. Routing selects a retrieval strategy and does not itself answer the user.

## System context

```mermaid
flowchart LR
  USER[User] --> UI[Streamlit]
  UI -->|HTTP POST /ask| API[FastAPI]
  API --> PIPE[RAG Pipeline]
  PIPE --> RET[Retrieval modules]
  RET --> DB[(ChromaDB)]
  PIPE --> CHAT[Ollama Qwen chat]
  DOCS[TXT source documents] --> WATCH[Watchdog]
  WATCH --> ING[Ingestion]
  ING --> EMB[Ollama Nomic embeddings]
  EMB --> DB
  API -. request IDs and events .-> LOG[Rotating logs]
  PIPE -. timings and events .-> LOG
```

In the current Mac Docker setup, API and frontend are Compose services. Ollama is a separately running container reachable from the API through `host.docker.internal:11434`.

## Component relationships

```mermaid
flowchart TB
  FE[frontend.py] --> MAIN[main.py]
  MAIN --> PIPE[rag_pipeline.py]
  MAIN --> WATCH[document_watcher.py]
  WATCH --> ING[ingestion.py]
  ING --> CHUNK[chunking.py]
  ING --> DB[(ChromaDB)]
  ING --> EMB[Ollama embeddings]
  PIPE --> INTENT[intent_router.py]
  PIPE --> SCOPE[scope_guard.py]
  PIPE --> ROUTER[retrieval_router.py]
  PIPE --> ADV[advanced_retrieval.py]
  PIPE --> MULTI[multi_query_retrieval.py]
  ADV --> HYBRID[hybrid_retrieval.py]
  MULTI --> HYBRID
  ADV --> RERANK[reranking.py]
  MULTI --> RERANK
  HYBRID --> DB
  PIPE --> GEN[generation.py]
  GEN --> CHAT[Ollama chat]
  MAIN -.-> OBS[observability.py]
  PIPE -.-> OBS
```

`query_rewriting.py` exists as a standalone utility; the active pipeline does not call its `rewrite_query()` function. Multi-query retrieval has its own query generation and reranking-query preparation.

## Request sequence

```mermaid
sequenceDiagram
  actor User
  participant UI as Streamlit
  participant API as FastAPI
  participant P as RAG pipeline
  participant R as Retrieval router
  participant DB as ChromaDB
  participant L as Ollama chat model
  User->>UI: Ask question
  UI->>API: POST /ask
  API->>API: Validate schema and create request ID
  API->>P: ask_question(question, request_id)
  P->>P: Intent classification
  P->>P: Scope validation
  P->>R: Choose single_query or multi_query
  R->>L: Request structured routing decision
  L-->>R: Strategy and reason
  P->>DB: Retrieve candidate chunks (through retrieval modules)
  DB-->>P: Ranked evidence
  P->>L: Question plus retrieved context
  L-->>P: Grounded answer
  P-->>API: Answer and source filenames
  API-->>UI: JSON plus X-Request-ID
  UI-->>User: Answer and sources
```

## Request stages

1. FastAPI validates `QuestionRequest`.
2. Middleware generates a UUID and starts request timing.
3. `ask_question` delegates to `process_question`.
4. Intent handling short-circuits invalid input and exact greetings.
5. The keyword scope guard checks the configured enterprise domain.
6. LLM routing chooses single- or multi-query retrieval.
7. Retrieval produces candidates, fused rankings, and reranker scores.
8. The pipeline joins selected chunk text into context.
9. Generation uses a grounding-oriented system prompt.
10. Unique source filenames are returned.
11. Middleware logs status and duration and returns `X-Request-ID`.

## Ingestion workflow

```mermaid
flowchart TD
  A[TXT directory] --> B[Load documents]
  B --> C[SHA-256 content hash]
  C --> D{Existing hash matches?}
  D -->|Yes| E[Skip unchanged]
  D -->|No| F[Recursive chunking]
  F --> G[Deduplicate exact chunks]
  G --> H[Generate all embeddings]
  H --> I{Embedding success?}
  I -->|No| J[Keep previous chunks]
  I -->|Yes| K[Delete previous source chunks]
  K --> L[Upsert new chunks and metadata]
  B --> M[Compare local and indexed filenames]
  M --> N[Delete chunks for missing files]
  E --> Z[Summary]
  J --> Z
  L --> Z
  N --> Z
```

Each chunk has an ID `filename_index`, text, vector, and metadata `source`, `chunk_index`, and `content_hash`.

### Replacement safety boundary

All embeddings for a changed file are generated before its existing chunks are deleted. Thus an embedding-generation exception leaves old records intact. ChromaDB deletion and upsert are separate operations, however; a write failure after deletion is not rolled back. This is not a transactional replacement.

## Watcher and FastAPI lifecycle

```mermaid
stateDiagram-v2
  [*] --> Startup
  Startup --> ObserverStarted
  ObserverStarted --> InitialSync
  InitialSync --> Ready
  Ready --> EventDetected
  EventDetected --> Debouncing
  Debouncing --> Ingesting
  Ingesting --> Ready
  Ready --> Shutdown
  Debouncing --> Shutdown: cancel timer
  Ingesting --> Shutdown: wait for lock
  Shutdown --> Stopped
  Stopped --> [*]
```

FastAPI lifespan starts the observer and performs initial sync before serving. At shutdown it stops and joins the observer, cancels pending timer work, and waits for active ingestion. The handler debounces TXT events and serializes watcher-triggered ingestion.

Local testing verified create, modify, delete, and graceful shutdown. Multiple events around one save caused more than one ingestion run in testing; event coalescing remains an improvement.

The watcher is process-local. The current Compose command uses one Uvicorn worker. Multiple workers would each create an observer; a multi-worker deployment should move watching to a dedicated service or add coordination.

## Container architecture

```mermaid
flowchart TB
  subgraph Host[macOS host]
    B[Browser]
    SRC[./data/documents]
    subgraph Docker[Docker Desktop Linux environment]
      FE[Frontend :8501]
      API[API :8000]
      CV[(chroma_data volume)]
      LV[(logs_data volume)]
    end
    O[Ollama :11434]
  end
  B -->|localhost:8501| FE
  B -->|localhost:8000| API
  FE -->|api:8000| API
  SRC <-->|bind mount| API
  API --> CV
  API --> LV
  API -->|host.docker.internal:11434| O
```

The documents path is a bind mount. ChromaDB and logs use named volumes. A bind mount synchronizes files; it does not itself create embeddings. Watchdog detects the event, ingestion calls Ollama, and ChromaDB receives the vectors.

## Health and readiness

The current `/health` endpoint confirms HTTP application responsiveness. It does not prove Ollama is reachable, models are loaded, the ChromaDB collection exists, or retrieval works. A dependency-aware readiness endpoint is a future improvement.

## Future architecture work

- Versioned or staged ChromaDB replacement for stronger write-failure recovery.
- Dedicated watcher service for multiple API workers.
- Stable-file detection for editors that write temporary files and rename them.
- PDF, DOCX, HTML, and scanned-document ingestion.
- Page/chunk citations.
- Persistent BM25 index or dedicated hybrid search engine.
- Larger retrieval and answer evaluation.
- Dependency-aware readiness checks and metrics.
