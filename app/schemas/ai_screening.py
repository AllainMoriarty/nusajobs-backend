from pydantic import BaseModel
from uuid import UUID
from typing import List
from datetime import datetime


class InterviewQuestionResponse(BaseModel):
    candidate_id: UUID
    questions: List[str]


class AIScreeningItemResponse(BaseModel):
    job_application_id: UUID
    candidate_id: UUID
    score: float
    rank: int
    reasoning: str


class AIScreeningResponse(BaseModel):
    job_id: UUID
    screenings: List[AIScreeningItemResponse]
    interview_questions: List[InterviewQuestionResponse]
    generated_at: datetime
