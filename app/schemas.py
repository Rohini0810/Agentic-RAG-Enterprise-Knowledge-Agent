#Step 2 — API request and response schemas
#Before writing the /ask endpoint, we need to understand how data enters and leaves our API.
#schemas.py will define:
#- QuestionRequest: what the frontend sends.
#- QuestionResponse: what the backend returns.
#We'll use Pydantic models for validation.
# What these models do:
#- QuestionRequest validates incoming questions.
#- min_length=1 prevents empty questions.
#- QuestionResponse defines the structure of the API response.
#- list[str] means the response can contain multiple source filenames.

from pydantic import BaseModel, Field


class QuestionRequest(BaseModel):
    question: str = Field(
        ...,
        min_length=1,
        description="Question asked by the user"
    )


class QuestionResponse(BaseModel):
    answer: str
    sources: list[str]