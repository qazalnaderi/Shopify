from pydantic import BaseModel
from typing import Optional
from uuid import UUID
from datetime import datetime

class QuestionCreateSchema(BaseModel):
    website_id: UUID
    item_id: UUID
    question_text: str

class QuestionAnswerSchema(BaseModel):
    answer_text: str

class QuestionResponseSchema(BaseModel):
    question_id: UUID
    item_id: UUID
    website_id: UUID
    buyer_name: str
    question_text: str
    answer_text: Optional[str] = None
    created_at: datetime
    answered_at: Optional[datetime] = None