
from typing import Annotated, Optional, List
from uuid import UUID
from fastapi import Depends
from domain.models.item_image_model import ItemImage
from services.item_image_service import ItemImageService

class ItemImageMainService:
    def __init__(
        self,
        service: Annotated[ItemImageService, Depends()]
    ):
        self.service = service

    async def create(self, item_id: UUID, image_url: str, is_main: bool):
        return await self.service.create_item_image(item_id, image_url, is_main)

    async def get_image_by_id(self, image_id: UUID) -> Optional[ItemImage]:
        return await self.service.get_image_by_id(image_id)

    async def get_all_images(self, item_id: UUID) -> List[ItemImage]:
        return await self.service.get_item_images(item_id)


    async def delete(self, image_id: UUID):
        return await self.service.delete_image(image_id)

    async def set_main(self, image_id: UUID):
        return await self.service.set_main_image(image_id)

    async def clear_main(self, item_id: UUID):
        return await self.service.clear_main_image(item_id)
