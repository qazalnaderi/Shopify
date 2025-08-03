from infrastructure.repositories.favorite_repository import FavoriteRepository
from uuid import UUID
from domain.models.favorite_model import Favorite
from fastapi import HTTPException, Depends
from typing import Annotated, List
from loguru import logger


class FavoriteService:
    def __init__(self, repo: Annotated[FavoriteRepository, Depends()]):
        self.repo = repo

    async def create(self, buyer_id: UUID, item_id: UUID) -> Favorite:
        return self.repo.create(buyer_id, item_id)

    async def get_all_by_buyer(self, buyer_id: UUID):
        return self.repo.get_by_buyer(buyer_id)

    async def get_by_buyer_and_item(self, buyer_id:UUID, item_id:UUID):
        return self.repo.get_by_buyer_and_item(buyer_id, item_id)

    async def delete(self, favorite_id: UUID, buyer_id: UUID) -> bool:
        return self.repo.delete(favorite_id, buyer_id)
