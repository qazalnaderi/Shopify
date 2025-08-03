from typing import Annotated, Optional
from fastapi import Depends
from sqlalchemy.orm import Session
from core.postgres_db.database import get_db
from domain.models.review_model import Review
from uuid import UUID
from sqlalchemy import func
from decimal import Decimal
class ReviewRepository:
    def __init__(self, db: Annotated[Session, Depends(get_db)]):
        self.db = db

    def create_review(self, buyer_id:UUID, website_id:UUID, item_id:UUID, rating:int, text:str):
        review = Review(
            buyer_id=buyer_id,
            website_id=website_id,
            item_id=item_id,
            rating=rating,
            text=text
        )
        self.db.add(review)
        self.db.commit()
        self.db.refresh(review)
        return review
    
    def get_review_by_id(self, review_id:UUID):
        return self.db.query(Review).filter(Review.review_id == review_id).first()
    
    def get_reviews_by_item(self, item_id:UUID):
        return self.db.query(Review).filter(Review.item_id == item_id).order_by(Review.created_at.desc()).all()
    

    def get_review_by_buyer_and_item(self, buyer_id: UUID, item_id: UUID) -> Optional[Review]:
      return (
          self.db.query(Review)
          .filter(Review.buyer_id == buyer_id, Review.item_id == item_id)
          .first()
      )
    
    def get_rating_for_item(self, item_id:UUID)->Decimal:
       rate = self.db.query(func.avg(Review.rating)).filter(Review.item_id == item_id).scalar() or 0
       return rate