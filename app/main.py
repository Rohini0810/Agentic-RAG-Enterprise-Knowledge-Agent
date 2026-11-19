
import time

from fastapi import FastAPI, Request

from app.schemas import QuestionRequest, QuestionResponse
from app.rag_pipeline import ask_question
from app.observability import generate_request_id, log_event


app = FastAPI(
    title="Agentic RAG API",
    description="Enterprise Knowledge Assistant",
    version="1.0.0"
)


@app.middleware("http")
async def observability_middleware(request: Request, call_next):
    # Generate one unique ID for every incoming HTTP request.
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

        # Return the same ID in the HTTP response header.
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

    # Pass the API request ID into the RAG pipeline.
    # This lets API logs and RAG logs share the same ID.
    result = ask_question(
        request.question,
        request_id=request_id
    )

    return QuestionResponse(
        answer=result["answer"],
        sources=result["sources"]
    )
