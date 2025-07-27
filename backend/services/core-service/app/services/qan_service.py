
from app.domain.models.review_model import Review
from loguru import logger
from app.infrastructure.repositories.qan_repository import QuestionRepository
from typing import Annotated, List, Optional
from fastapi import HTTPException, Depends
from app.domain.schemas.qan_schema import QuestionCreateSchema, QuestionAnswerSchema
from app.domain.models.qan_model import ItemQuestion
from app.services.user_service import UserService
from uuid import UUID
from app.services.plan_service import PlanService
class QuestionService:
    def __init__(self,
                  question_epository: Annotated[QuestionRepository, Depends()],
                  user_service: Annotated[UserService, Depends()],
                  plan_service: Annotated[PlanService, Depends()]
                  ):
        self.question_epository = question_epository
        self.user_service = user_service
        self.plan_service = plan_service


    async def create_question(self, buyer_id: UUID, data: QuestionCreateSchema) -> ItemQuestion:
        website_plan = await self.plan_service.get_active_plan_by_website_id(data.website_id)
        plan = await self.plan_service.get_plan_by_id(website_plan.plan_id)
        if plan.name != 'Pro':
            raise HTTPException(status_code=403, detail="Asking questions is only available in pro plan.")

        return self.question_epository.create_question(buyer_id, data)

    async def answer_question(self,user_id:UUID, question_id: UUID, data: QuestionAnswerSchema) -> ItemQuestion:
        question = await self.get_question_by_id(question_id)
        if not question:
            raise HTTPException(status_code=404, detail="Question not found.")
        user_website = await self.user_service.check_is_owner(user_id)
        if user_website.website_id != question.website_id:
            raise HTTPException(status_code=403, detail="You are not allowed to answer this question.")
        return self.question_epository.answer_question(question_id, data)
    
    async def get_question_by_id(self, question_id: UUID) -> ItemQuestion:
        question = self.question_epository.get_question_by_id(question_id)
        if not question:
            raise HTTPException(status_code=404, detail="Question not found.")
        return question
    

    async def get_question_by_item_id(self, item_id: UUID) -> List[ItemQuestion]:
        return self.question_epository.get_question_by_item_id(item_id)