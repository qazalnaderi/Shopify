from fastapi import APIRouter, Depends, HTTPException, status
from services.item_main_service import ItemMainService
from domain.schemas.item_schema import ItemCreateSchema,ItemResponseWithRateSchema, ItemResponseSchema,NewestItemResponseSchema, ItemUpdateSchema, MessageResponse, ItemResponseWithNameSchema
from services.auth_services.user_auth_service import get_current_user
from domain.schemas.token_schema import TokenDataSchema
from loguru import logger
from typing import Annotated, List
from uuid import UUID

item_router = APIRouter()

@item_router.post("/create_item", response_model=ItemResponseSchema, status_code=status.HTTP_201_CREATED)
async def create_item(
    item_data: ItemCreateSchema,
    current_user: Annotated[TokenDataSchema, Depends(get_current_user)],
    item_service: Annotated[ItemMainService, Depends()]
):
    logger.info(f"User with id: {current_user.user_id} is creating an item with data: {item_data.dict()}")

    created_item = await item_service.create_item(item_data)
    return created_item


@item_router.get("/items/{item_id}", response_model=NewestItemResponseSchema, status_code=status.HTTP_200_OK)
async def get_item_by_id(
    item_id: UUID,
    item_main_service: Annotated[ItemMainService, Depends()]
):
    logger.info(f"Fetching item with ID: {item_id}")
    item_response = await item_main_service.get_item_by_id(item_id)
    return item_response


@item_router.get("/items/by_category/{category_id}", response_model=List[ItemResponseSchema], status_code=status.HTTP_200_OK)
async def get_items_by_category(
    category_id: UUID,
    item_main_service: Annotated[ItemMainService, Depends()]
):
    return await item_main_service.get_items_by_category_id(category_id)

@item_router.get("/items/by_subcategory/{subcategory_id}", response_model=List[ItemResponseSchema], status_code=status.HTTP_200_OK)
async def get_items_by_subcategory(
    subcategory_id: UUID,
    item_main_service: Annotated[ItemMainService, Depends()]
):
    return await item_main_service.get_items_by_subcategory_id(subcategory_id)



@item_router.put("/edit_item/{item_id}", response_model=ItemResponseSchema, status_code=status.HTTP_200_OK)
async def edit_item(
    item_id: UUID,
    item_data: ItemUpdateSchema,
    current_user: Annotated[TokenDataSchema, Depends(get_current_user)],
    item_service: Annotated[ItemMainService, Depends()],
):
    logger.info(f"User with id: {current_user.user_id} is requesting to edit item with ID: {item_id}")
    
    return await item_service.edit_item(item_id, item_data)


@item_router.delete("/delete_item/{item_id}", response_model=MessageResponse, status_code=status.HTTP_200_OK)
async def delete_item(
    item_id: UUID,
    current_user: Annotated[TokenDataSchema, Depends(get_current_user)],
    item_service: Annotated[ItemMainService, Depends()],
):
    logger.info(f"User with id: {current_user.user_id} is requesting to delete item with ID: {item_id}")
    
    return await item_service.delete_item(item_id)



@item_router.get("/newest_items", response_model=List[NewestItemResponseSchema], status_code=status.HTTP_200_OK)
async def get_newest_items(website_id: UUID, limit:int, item_main_service: ItemMainService = Depends()):
    return await item_main_service.get_newest_items(website_id, limit)


@item_router.get("/items/count/{website_id}")
async def get_items_count(
    website_id: UUID,
    current_user: Annotated[TokenDataSchema, Depends(get_current_user)],
    item_service: Annotated[ItemMainService, Depends()],
):
    count = await item_service.get_items_count(website_id)
    return {"items_count": count}



@item_router.get("/items/item-count/{category_id}")
async def get_item_count_by_category_id(
    category_id: UUID,
    current_user: Annotated[TokenDataSchema, Depends(get_current_user)],
    item_service: Annotated[ItemMainService, Depends()],
):
    return await item_service.get_item_count_by_category_id(category_id)