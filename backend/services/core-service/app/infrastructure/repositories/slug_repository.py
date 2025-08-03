from fastapi import Depends
from sqlalchemy.orm import Session
from core.postgres_db.database import get_db
from domain.models.slug_model import SlugModel
from typing import Optional, Annotated
from uuid import UUID

class SlugRepository:
    def __init__(self, db: Annotated[Session, Depends(get_db)]):
        self.db = db

    def exists(self, slug: str) -> bool:
        return self.db.query(SlugModel).filter_by(slug=slug).first() is not None

    def create(self, slug:SlugModel):
        self.db.add(slug)
        self.db.commit()

    def get_slug(self, slug: str) -> Optional[UUID]:
        entry = self.db.query(SlugModel).filter_by(slug=slug).first()
        return entry
    
    def get_slug_by_website_id(self, website_id: UUID) -> Optional[UUID]:
        return self.db.query(SlugModel).filter_by(website_id=website_id).first()


    def update_slug_by_website_id(self, website_id: UUID, new_slug: str):
        slug = self.db.query(SlugModel).filter_by(website_id=website_id).first()
        slug.slug = new_slug
        self.db.add(slug)
        self.db.commit()
        self.db.refresh(slug)
