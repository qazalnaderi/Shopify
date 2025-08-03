from fastapi import APIRouter, Depends, status
from typing import List
from uuid import UUID
from domain.schemas.favorite_schema import FavoriteResponseSchema
from services.favorite_main_service import FavoriteMainService
from services.auth_services.buyer_auth_service import get_current_buyer
from domain.schemas.token_schema import TokenDataSchema
from typing import Annotated

favorite_router = APIRouter()

@favorite_router.post("/", response_model=FavoriteResponseSchema, status_code=status.HTTP_201_CREATED)
async def create_favorite(
    item_id: UUID,
    current_buyer: Annotated[TokenDataSchema, Depends(get_current_buyer)],
    service: Annotated[FavoriteMainService, Depends()],
):
    return await service.create_favorite(current_buyer.buyer_id, item_id)

@favorite_router.get("/", response_model=List[FavoriteResponseSchema])
async def get_favorites(
    current_buyer: Annotated[TokenDataSchema, Depends(get_current_buyer)],
    service: Annotated[FavoriteMainService, Depends()],
):
    return await service.get_favorites_by_buyer(current_buyer.buyer_id)

@favorite_router.delete("/delete/{favorite_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_favorite(
    favorite_id: UUID,
    current_buyer: Annotated[TokenDataSchema, Depends(get_current_buyer)],
    service: Annotated[FavoriteMainService, Depends()],
):
    await service.delete_favorite(favorite_id, current_buyer.buyer_id)
    return {"detail": "Favorite deleted successfully"}