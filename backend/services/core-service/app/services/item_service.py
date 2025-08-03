from infrastructure.repositories.item_repository import ItemRepository
from domain.models.website_model import Item
from domain.schemas.item_schema import ItemCreateSchema,ItemUpdateSchema
from uuid import UUID
from fastapi import HTTPException, Depends
from services.base_service import BaseService
from typing import Annotated, List, Dict
from loguru import logger

class ItemService(BaseService):
    def __init__(
        self,
        item_repository: Annotated[ItemRepository, Depends()],
    ) -> None:
        super().__init__()  
        self.item_repository = item_repository

    async def create_item(self, item_data: ItemCreateSchema) -> Item:
      

      item = Item(
          website_id=item_data.website_id,
          category_id=item_data.category_id,
          subcategory_id=item_data.subcategory_id,
          name=item_data.name,
          description=item_data.description,
          price=item_data.price,
          delivery_url=item_data.delivery_url,
          post_purchase_note=item_data.post_purchase_note,
          stock=item_data.stock
      )

      created_item = self.item_repository.create_item(item=item)
      logger.info(f"Item created successfully with ID: {created_item.item_id}")

      return created_item
    
    async def get_item_by_id(self, item_id: UUID) -> Item:
        logger.info(f"Fetching item with ID: {item_id}")
        item = self.item_repository.get_item_by_id(item_id)
        if not item:
                raise HTTPException(status_code=404, detail="No item found")
        return item


    async def get_items_by_subcategory_id(self, subcategory_id: UUID) -> List[Item]:
        items = self.item_repository.get_items_by_subcategory_id(subcategory_id)
        return items

        

    async def get_items_by_category_id(self, category_id: UUID) -> List[Item]:
        items = self.item_repository.get_items_by_category_id(category_id)
        return items

        

    async def edit_item(self, item_id: UUID, item_data: Dict) -> Item:
        logger.info(f"Updating item with ID: {item_id}")

        updated_item = self.item_repository.update_item(item_id, item_data)
        
        return updated_item    
    

    async def delete_item(self, item_id: UUID) -> bool:
        logger.info(f"Deleting item with ID: {item_id}")

        item = self.item_repository.get_item_by_id(item_id)
        self.item_repository.delete_item(item)
        return True
    

    async def get_newest_items(self, website_id: UUID, limit: int) -> List[Item]:
        logger.info(f"Fetching the first {limit} newest items")

        items = self.item_repository.get_newest_items(website_id, limit)
        return items
    

    async def get_items_count(self, website_id: UUID) -> int:
        return self.item_repository.get_items_count(website_id)

    async def get_item_count_by_category_id(self, category_id: UUID) -> int:
        return self.item_repository.get_item_count_by_category_id(category_id)
    

    async def reduce(self, item_id: UUID ,stock: int, is_available:bool):
        return self.item_repository.reduce(item_id,stock, is_available)