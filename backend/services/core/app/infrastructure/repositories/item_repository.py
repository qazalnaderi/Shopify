from app.domain.models.website_model import Item
from sqlalchemy.orm import Session
from loguru import logger
from uuid import UUID
from app.core.postgres_db.database import get_db
from typing import Annotated, Optional, List
from fastapi import Depends


class ItemRepository:
    def __init__(self, db: Annotated[Session, Depends(get_db)]):
        self.db = db

    def create_item(self, item: Item) -> Item:
      self.db.add(item)
      self.db.commit()
      self.db.refresh(item)
      logger.info(f"✅ Item created with id: {item.item_id}")
      return item
    
    def get_item_by_id(self, item_id: UUID) -> Optional[Item]:
        item = self.db.query(Item).filter(Item.item_id == item_id).first()
        if item:
            logger.info(f"Item found with id: {item_id}")
        else:
            logger.warning(f"No item found with id: {item_id}")
        return item
    
    def get_items_by_category_id(self, category_id: UUID) -> List[Item]:
        return self.db.query(Item).filter(Item.category_id == category_id).all()
    
    
    def get_items_by_subcategory_id(self, subcategory_id: UUID) -> List[Item]:
        return self.db.query(Item).filter(Item.subcategory_id == subcategory_id).all()
    

    def update_item(self, item: Item) -> Item:
        self.db.commit()
        self.db.refresh(item)
        return item
    

    def delete_item(self, item: Item) -> Item:
        self.db.delete(item)
        self.db.commit()
        return item
    

    def get_newest_items(self, website_id: UUID, limit: int) -> List[Item]:
        return (
            self.db.query(Item)
            .filter(Item.website_id == website_id)
            .order_by(Item.created_at.desc())
            .limit(limit)
            .all()
        )
    

    def count_items_by_website_id(self, website_id: UUID) -> int:
        return self.db.query(Item).filter(Item.website_id == website_id).count()
