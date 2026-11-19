
import asyncio
import logging
import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request

from app.schemas import QuestionRequest, QuestionResponse
from app.rag_pipeline import ask_question
from app.observability import generate_request_id, log_event
from app.ingestion import ingest_documents
from app.document_watcher import start_document_watcher


logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):

    lifecycle_id = generate_request_id()
    observer = None
    handler = None

    # -------------------------
    # APPLICATION STARTUP
    # -------------------------

    log_event(
        event="application_startup",
        request_id=lifecycle_id,
        message="Starting Agentic RAG API"
    )

    try:
        # Start document watcher.
        observer, handler = start_document_watcher()

        app.state.document_observer = observer
        app.state.document_handler = handler

        # Synchronize documents already present at startup.
        log_event(
            event="initial_document_sync_started",
            request_id=lifecycle_id
        )

        result = await asyncio.to_thread(ingest_documents)

        log_event(
            event="initial_document_sync_completed",
            request_id=lifecycle_id,
            result=result
        )

        log_event(
            event="application_started",
            request_id=lifecycle_id,
            message="Agentic RAG API is ready"
        )

        yield

    except Exception:
        logger.exception("Application lifecycle failed")

        log_event(
            event="application_lifecycle_failed",
            request_id=lifecycle_id,
            level="exception"
        )

        raise

    finally:
        # -------------------------
        # APPLICATION SHUTDOWN
        # -------------------------

        log_event(
            event="application_shutdown_started",
            request_id=lifecycle_id
        )

        if observer is not None:
            # Stop receiving filesystem events.
            observer.stop()

            # Wait for observer thread to terminate.
            await asyncio.to_thread(observer.join)

        if handler is not None:
            # Cancel pending timer and wait for active ingestion.
            await asyncio.to_thread(handler.shutdown)

        log_event(
            event="application_shutdown_completed",
            request_id=lifecycle_id,
            message="Document watcher stopped gracefully"
        )


app = FastAPI(
    title="Agentic RAG API",
    description="Enterprise Knowledge Assistant",
    version="1.0.0",
    lifespan=lifespan
)


@app.middleware("http")
async def observability_middleware(request: Request, call_next):

    request_id = generate_request_id()
    request.state.request_id = request_id

    start_time = time.perf_counter()

    log_event(
        event="api_request_started",
        request_id=request_id,
        method=request.method,
        path=request.url.path
    )

    try:
        response = await call_next(request)

        duration_ms = round(
            (time.perf_counter() - start_time) * 1000,
            2
        )

        response.headers["X-Request-ID"] = request_id

        log_event(
            event="api_request_completed",
            request_id=request_id,
            method=request.method,
            path=request.url.path,
            status_code=response.status_code,
            duration_ms=duration_ms
        )

        return response

    except Exception:

        duration_ms = round(
            (time.perf_counter() - start_time) * 1000,
            2
        )

        log_event(
            event="api_request_failed",
            request_id=request_id,
            level="exception",
            method=request.method,
            path=request.url.path,
            duration_ms=duration_ms
        )

        raise


@app.get("/health")
def health_check():

    return {
        "status": "healthy",
        "application": "Agentic RAG"
    }


@app.post("/ask", response_model=QuestionResponse)
def ask(request: QuestionRequest, http_request: Request):

    request_id = http_request.state.request_id

    result = ask_question(
        request.question,
        request_id=request_id
    )

    return QuestionResponse(
        answer=result["answer"],
        sources=result["sources"]
    )
