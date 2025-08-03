from domain.models.website_model import Item
from sqlalchemy.orm import Session
from loguru import logger
from uuid import UUID
from core.postgres_db.database import get_db
from typing import Annotated, Optional, List
from fastapi import Depends
from sqlalchemy import func


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
    

    def update_item(self, item_id: UUID, updated_item) -> Item:
        item_query = self.db.query(Item).filter(Item.item_id == item_id)
        db_item = item_query.first()

        if db_item:
            item_query.update(updated_item, synchronize_session=False)
            self.db.commit()
            self.db.refresh(db_item)
            logger.info(f"✅ item {item_id} updated")
            return db_item
        else:
            logger.warning(f"⚠️ item {item_id} not found")
            return None
    

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

    def get_items_count(self, website_id: UUID) -> int:
        count = self.db.query(func.count(Item.item_id)).filter(
            Item.website_id == website_id
        ).scalar() or 0
        return count
    
    def activate_discount(self, item_id: UUID, percent:int):
        item = self.get_item_by_id(item_id)    
        discount_price = float(item.price) * (1 - percent / 100)
        item.discount_price = round(discount_price, 2)

        if percent <= 0 or percent >= 100:
            raise ValueError("Must be between 1-99")
        
        item.discount_active = True
        item.discount_percent = percent
        item.discount_price = round(discount_price, 2)
        
        self.db.commit()
        self.db.refresh(item)

    def get_item_count_by_category_id(self, category_id: UUID) -> int:
        count = self.db.query(func.count(Item.item_id)).filter(
            Item.category_id == category_id
        ).scalar() or 0
        return count
    

    def reduce(self, item_id: UUID, stock: int, is_available:bool)-> Item:
        item = self.get_item_by_id(item_id)  
        item.stock = stock
        item.is_available= is_available

        self.db.commit()
        self.db.refresh(item)