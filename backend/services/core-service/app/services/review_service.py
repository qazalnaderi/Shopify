
from domain.models.review_model import Review
from loguru import logger
from infrastructure.repositories.review_repository import ReviewRepository
from typing import Annotated, List, Optional
from fastapi import HTTPException, Depends
from uuid import UUID
from decimal import Decimal

class ReviewService:
    def __init__(self,
        review_repository: Annotated[ReviewRepository, Depends()],
        ):
        self.review_repository = review_repository

    async def create_review(self, buyer_id:UUID, website_id:UUID, item_id:UUID, rating:int, text:str) -> Review:
        existing = self.review_repository.get_review_by_buyer_and_item(buyer_id, item_id)
        if existing:
            raise HTTPException(status_code=409, detail="You have already submitted a review for this item.")

        created_review = self.review_repository.create_review(buyer_id, website_id, item_id, rating, text)
        logger.info(f"Review created for item {created_review.item_id} by buyer {created_review.buyer_id}")
        return created_review
    

    async def get_review_by_id(self, review_id:UUID) -> Review:
        review = self.review_repository.get_review_by_id(review_id)
        if not review:
            raise HTTPException(status_code=404, detail="Review not found")
        return review


    async def get_item_reviews(self, item_id:UUID) -> List[Review]:
        reviews = self.review_repository.get_reviews_by_item(item_id)
        return reviews

    async def get_review_by_buyer_and_item(self, buyer_id: UUID, item_id: UUID) -> Optional[Review]:
        return self.review_repository.get_review_by_buyer_and_item(buyer_id, item_id)

    async def get_rating_for_item(self, item_id: UUID) -> Decimal:
        return self.review_repository.get_rating_for_item(item_id)
    

