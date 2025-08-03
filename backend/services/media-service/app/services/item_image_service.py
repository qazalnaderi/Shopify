from uuid import UUID, uuid4
from typing import Annotated, Optional, List
from fastapi import Depends
from infrastructure.repositories.item_image_repository import ItemImageRepository
from domain.models.item_image_model import ItemImage


class ItemImageService:
    def __init__(self, item_image_repo: Annotated[ItemImageRepository, Depends()]):
        self.repo = item_image_repo

    async def create_item_image(self, item_id: UUID, image_url: str, is_main: bool):
        return self.repo.create_item_image(image_id=uuid4(),
            item_id=item_id,
            image_url=image_url,
            is_main=is_main)

    async def delete_image(self, image_id: UUID):
        image = self.repo.get_by_id(image_id)
        if not image:
            raise Exception("Image not found")
        self.repo.delete(image_id)

    async def set_main_image(self, image_id: UUID):
        image = self.repo.get_by_id(image_id)
        if not image:
            raise Exception("Image not found")

        self.repo.clear_main_for_item(image.item_id)
        self.repo.set_main(image_id)

    async def clear_main_image(self, item_id: UUID):
        self.repo.clear_main_for_item(item_id)

    async def get_image_by_id(self, image_id: UUID) -> Optional[ItemImage]:
        return self.repo.get_by_id(image_id)

    async def get_item_images(self, item_id: UUID) -> List[ItemImage]:
        return self.repo.get_by_item_id(item_id)

