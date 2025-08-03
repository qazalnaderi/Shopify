from fastapi import APIRouter, Depends, status
from typing import Annotated, List
from domain.schemas.review_schema import ReviewCreateSchema, ReviewResponseSchema
from services.auth_services.buyer_auth_service import get_current_buyer
from domain.schemas.token_schema import TokenDataSchema
from services.auth_services.user_auth_service import get_current_user
from services.review_main_service import ReviewMainService
from uuid import UUID
from loguru import logger


review_router = APIRouter()

@review_router.post("/create_review", response_model=ReviewResponseSchema, status_code=status.HTTP_201_CREATED)
async def create_review(
    review: ReviewCreateSchema,
    current_buyer: Annotated[TokenDataSchema, Depends(get_current_buyer)],
    review_service: Annotated[ReviewMainService, Depends()]
):
    logger.info(f"Buyer {current_buyer.buyer_id} is submitting review for item {review.item_id}")

    return await review_service.create_review(
        buyer_id=current_buyer.buyer_id,
        website_id=review.website_id,
        item_id=review.item_id,
        rating=review.rating,
        text=review.text)


@review_router.get("/reviews/{review_id}", response_model=ReviewResponseSchema)
async def get_review(
    review_id: UUID,
    review_main_service: Annotated[ReviewMainService, Depends()]
):
    return await review_main_service.get_review_by_id(review_id)



@review_router.get("/items/{item_id}/reviews", response_model=List[ReviewResponseSchema])
async def get_item_reviews(
    item_id: UUID,
    review_main_service: Annotated[ReviewMainService, Depends()]
):
    return await review_main_service.get_reviews_for_item(item_id)


@review_router.get("/items/get-rating/{item_id}")
async def get_rating(
    item_id: UUID,
    review_main_service: Annotated[ReviewMainService, Depends()],
    current_user: Annotated[TokenDataSchema, Depends(get_current_user)],

):
    rate = await review_main_service.get_rating_for_item(item_id)
    return {"rating": rate}