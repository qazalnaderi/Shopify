from sqlalchemy.orm import Session
from uuid import UUID
from typing import List, Annotated, Optional
from domain.models.item_image_model import ItemImage   
from fastapi import Depends
from sqlalchemy.orm import Session
from core.postgres_db.postgres_database import get_db
from loguru import logger
class ItemImageRepository:
    def __init__(self, db: Annotated[Session, Depends(get_db)]):
        self.db = db

    def create_item_image(self,
            image_id:str,
            item_id:UUID,
            image_url:str,
            is_main:bool
        ):
        image = ItemImage(
            image_id=image_id,
            item_id=item_id,
            image_url=image_url,
            is_main=is_main
        )
        self.db.add(image)
        self.db.commit()

    def get_by_item_id(self, item_id: UUID) -> List[ItemImage]:
        return self.db.query(ItemImage).filter(ItemImage.item_id == item_id).all()


    def delete(self, image_id: UUID):
        self.db.query(ItemImage).filter(ItemImage.image_id == image_id).delete()
        self.db.commit()

    def clear_main_for_item(self, item_id: UUID):
        self.db.query(ItemImage).filter(
            ItemImage.item_id == item_id, ItemImage.is_main == True
        ).update({ItemImage.is_main: False}, synchronize_session=False)
        self.db.commit()

    def set_main(self, image_id: UUID):
        self.db.query(ItemImage).filter(
            ItemImage.image_id == image_id
        ).update({ItemImage.is_main: True}, synchronize_session=False)
        self.db.commit()


    def get_by_id(self, image_id: UUID) -> Optional[ItemImage]:
        return self.db.query(ItemImage).filter(ItemImage.image_id == image_id).first()

    def get_by_item_id(self, item_id: UUID) -> List[ItemImage]:
        logger.info(f"Querying for item_id: {item_id}")
        return self.db.query(ItemImage).filter(ItemImage.item_id == item_id).all()
    
