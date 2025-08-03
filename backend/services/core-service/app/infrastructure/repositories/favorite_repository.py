from sqlalchemy.orm import Session
from domain.models.favorite_model import Favorite
from uuid import UUID
from core.postgres_db.database import get_db
from typing import Annotated, Optional, List
from fastapi import Depends
from loguru import logger

class FavoriteRepository:
    def __init__(self, db: Annotated[Session, Depends(get_db)]):
        self.db = db

    def create(self, buyer_id: UUID, item_id: UUID) -> Favorite:
        favorite = Favorite(buyer_id=buyer_id, item_id=item_id)
        self.db.add(favorite)
        self.db.commit()
        self.db.refresh(favorite)
        return favorite

    def get_by_buyer(self, buyer_id: UUID):
        return self.db.query(Favorite).filter(Favorite.buyer_id == buyer_id).all()
    
    def get_by_buyer_and_item(self, buyer_id: UUID, item_id: UUID):
        return self.db.query(Favorite).filter(Favorite.buyer_id == buyer_id, Favorite.item_id== item_id).first()
    
    def delete(self, favorite_id: UUID, buyer_id: UUID) -> bool:
        favorite = self.db.query(Favorite).filter(Favorite.id == favorite_id, Favorite.buyer_id == buyer_id).first()
        if favorite:
            self.db.delete(favorite)
            self.db.commit()
            return True
        return False
