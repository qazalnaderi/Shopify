from fastapi import APIRouter, Depends, status
from typing import Annotated, List
from domain.schemas.qan_schema import QuestionCreateSchema, QuestionResponseSchema, QuestionAnswerSchema
from services.auth_services.buyer_auth_service import get_current_buyer
from services.auth_services.user_auth_service import  get_current_user
from domain.schemas.token_schema import TokenDataSchema
from services.qan_main_service import QuestionMainService
from uuid import UUID
from loguru import logger


qan_router = APIRouter()

@qan_router.post("/create_question", response_model=QuestionResponseSchema, status_code=status.HTTP_201_CREATED)
async def create_question(
    question: QuestionCreateSchema,
    current_buyer: Annotated[TokenDataSchema, Depends(get_current_buyer)],
    question_service: Annotated[QuestionMainService, Depends()]
):
    logger.info(f"Buyer {current_buyer.buyer_id} is asking question for item {question.item_id}")
    return await question_service.ask_question(
        buyer_id=current_buyer.buyer_id,
        data=question
    )


@qan_router.patch("/questions/{question_id}/answer", response_model=QuestionResponseSchema)
async def answer_question(
    question_id: UUID,
    data: QuestionAnswerSchema,
    current_user: Annotated[TokenDataSchema, Depends(get_current_user)],
    question_service: Annotated[QuestionMainService, Depends()]
):
    return await question_service.answer_question(current_user.user_id, question_id, data.answer_text)


@qan_router.get("/questions/{question_id}", response_model=QuestionResponseSchema)
async def get_question_by_id(
    question_id: UUID,
    question_service: Annotated[QuestionMainService, Depends()]
):
    return await question_service.get_question_by_id(question_id)

@qan_router.get("/items/{item_id}/questions", response_model=List[QuestionResponseSchema])
async def get_question_by_item_id(
    item_id: UUID,
    question_service: Annotated[QuestionMainService, Depends()]
):
    return await question_service.get_question_by_item_id(item_id)
