from pydantic import BaseModel
from uuid import UUID
from datetime import datetime


class ReviewCreateSchema(BaseModel):
    website_id: UUID
    item_id: UUID 
    rating: int 
    text: str

class ReviewResponseSchema(BaseModel):
    review_id: UUID
    item_id: UUID
    buyer_id: UUID
    buyer_name: str
    website_id: UUID
    rating: int
    text: str
    created_at: datetime

