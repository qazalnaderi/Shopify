from typing import Annotated, List
from fastapi import Depends
from sqlalchemy.orm import Session
from core.postgres_db.database import get_db
from domain.models.qan_model import ItemQuestion
from uuid import UUID
from datetime import datetime

from domain.schemas.qan_schema import QuestionCreateSchema


class QuestionRepository:
    def __init__(self, db: Annotated[Session, Depends(get_db)]):
        self.db = db

    def create_question(self, buyer_id: UUID, data: QuestionCreateSchema) -> ItemQuestion:
        question = ItemQuestion(
            item_id=data.item_id,
            buyer_id=buyer_id,
            website_id=data.website_id,
            question_text=data.question_text,
            created_at=datetime.utcnow()
        )
        self.db.add(question)
        self.db.commit()
        self.db.refresh(question)
        return question

    def answer_question(self, question_id: UUID, answer_text: str) -> ItemQuestion:
      question = self.db.query(ItemQuestion).get(question_id)
      question.answer_text = answer_text
      question.answered_at = datetime.utcnow()
      self.db.commit()
      self.db.refresh(question)
      return question
    
    def get_question_by_id(self, question_id: UUID) -> ItemQuestion:
        return self.db.query(ItemQuestion).get(question_id)
    

    def get_question_by_item_id(self, item_id: UUID) -> List[ItemQuestion]:
        return self.db.query(ItemQuestion).filter(ItemQuestion.item_id == item_id).all()
    