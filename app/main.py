
from fastapi import FastAPI

from app.schemas import QuestionRequest, QuestionResponse
from app.rag_pipeline import ask_question

app = FastAPI(
    title="Agentic RAG API",
    description="Enterprise Knowledge Assistant",
    version="1.0.0"
)


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "application": "Agentic RAG"
    }


@app.post("/ask", response_model=QuestionResponse)
def ask(request: QuestionRequest):
    result = ask_question(request.question)

    return QuestionResponse(
        answer=result["answer"],
        sources=result["sources"]
    )
