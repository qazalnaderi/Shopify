from loguru import logger
from services.favorite_service import FavoriteService
from uuid import UUID
from domain.schemas.favorite_schema import FavoriteResponseSchema
from typing  import Annotated, List
from fastapi import HTTPException, Depends

class FavoriteMainService:
    def __init__(self, service: Annotated[FavoriteService, Depends()],
):
        self.service = service

    async def create_favorite(self, buyer_id: UUID, item_id: UUID) -> FavoriteResponseSchema:
        exists = await self.service.get_by_buyer_and_item(buyer_id, item_id)
        if exists:
            raise HTTPException(status_code=403, detail="You already did this.")
        
        favorite= await self.service.create(buyer_id, item_id)
        return FavoriteResponseSchema(
            id=favorite.id,
            item_id=favorite.item_id
        )
    
    async def get_favorites_by_buyer(self, buyer_id: UUID) -> List[FavoriteResponseSchema]:
        favs = await self.service.get_all_by_buyer(buyer_id)
        return [
            FavoriteResponseSchema(
                id=f.id,
                item_id=f.item_id,
            )
            for f in favs
        ]
    
    async def delete_favorite(self, favorite_id: UUID, buyer_id: UUID) -> bool:
        return await self.service.delete(favorite_id, buyer_id)
