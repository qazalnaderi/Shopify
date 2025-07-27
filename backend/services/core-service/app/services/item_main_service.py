from app.services.item_service import ItemService
from app.domain.schemas.item_schema import ItemCreateSchema, ItemResponseSchema, ItemUpdateSchema, MessageResponse, ItemResponseWithNameSchema
from uuid import UUID
from fastapi import HTTPException, Depends
from loguru import logger
from app.services.base_service import BaseService
from typing import Annotated, List, Dict
from app.services.website_service import WebsiteService
from app.services.plan_service import PlanService
from decimal import Decimal



class ItemMainService(BaseService):
    def __init__(
        self,
        item_service: Annotated[ItemService, Depends()],
        website_service: Annotated[WebsiteService, Depends()],
        plan_service: Annotated[PlanService, Depends()],
    ) -> None:
        super().__init__()
        self.item_service = item_service
        self.website_service = website_service
        self.plan_service =plan_service

    async def create_item(self, item_data: ItemCreateSchema) -> ItemResponseSchema:
        logger.info(f"Starting to create item... ")
        
        if item_data.stock <= 0:
            raise HTTPException(status_code=400, detail="Stock must be greater than zero")
        await self.plan_service.check_item_limit(item_data.website_id)


        created_item = await self.item_service.create_item(item_data)
    
        return ItemResponseSchema(
                item_id=created_item.item_id,
                website_id=created_item.website_id,
                category_id=created_item.category_id,
                subcategory_id=created_item.subcategory_id,
                name=created_item.name,
                description=created_item.description,
                price=created_item.price,
                discount_price=created_item.discount_price,
                discount_active=created_item.discount_active,
                discount_expires_at=created_item.discount_expires_at,
                delivery_url=created_item.delivery_url,
                post_purchase_note=created_item.post_purchase_note,
                stock=created_item.stock,
                is_available=created_item.is_available,
                created_at=created_item.created_at,
            )    
        

        
    async def get_item_by_id(self, item_id: UUID) -> ItemResponseWithNameSchema:
        logger.info(f"Starting to fetch item with ID: {item_id}")

        item = await self.item_service.get_item_by_id(item_id)
        category = await self.website_service.get_category_by_id(item.category_id)
        subcategory = await self.website_service.get_subcategory_by_id(item.subcategory_id)
        return ItemResponseWithNameSchema(
            item_id=item.item_id,
            website_id=item.website_id,
            category_id=item.category_id,
            subcategory_id=item.subcategory_id,
            category_name=category.name if category else 'null',
            subcategory_name=subcategory.name if subcategory else 'null',
            name=item.name,
            description=item.description,
            price=item.price,
            discount_price=item.discount_price,
            discount_active=item.discount_active,
            discount_percent=item.discount_percent,
            discount_expires_at=item.discount_expires_at,
            delivery_url=item.delivery_url,
            post_purchase_note=item.post_purchase_note,
            stock=item.stock,
            is_available=item.is_available,
            created_at=item.created_at,
        )
    


    async def get_items_by_subcategory_id(self, subcategory_id: UUID) -> List[ItemResponseSchema]:
        logger.info(f"Starting to fetch items with subcategory id: {subcategory_id}")
        items = await self.item_service.get_items_by_subcategory_id(subcategory_id)

        return [
            ItemResponseSchema(
                item_id=item.item_id,
                website_id=item.website_id,
                category_id=item.category_id,
                subcategory_id=item.subcategory_id,
                name=item.name,
                description=item.description,
                price=item.price,
                discount_price=item.discount_price,
                discount_active=item.discount_active,
                discount_expires_at=item.discount_expires_at,
                delivery_url=item.delivery_url,
                post_purchase_note=item.post_purchase_note,
                stock=item.stock,
                is_available=item.is_available,
                created_at=item.created_at,
            )
            for item in items
        ]
    

    async def get_items_by_category_id(self, category_id: UUID) -> List[ItemResponseSchema]:
        logger.info(f"Starting to fetch items with subcategory id: {category_id}")
        items = await self.item_service.get_items_by_category_id(category_id)

        return [
            ItemResponseSchema(
                item_id=item.item_id,
                website_id=item.website_id,
                category_id=item.category_id,
                subcategory_id=item.subcategory_id,
                name=item.name,
                description=item.description,
                price=item.price,
                discount_price=item.discount_price,
                discount_active=item.discount_active,
                discount_percent=item.discount_percent,
                discount_expires_at=item.discount_expires_at,
                delivery_url=item.delivery_url,
                post_purchase_note=item.post_purchase_note,
                stock=item.stock,
                is_available=item.is_available,
                created_at=item.created_at,
            )
            for item in items
        ]



    async def edit_item(self, item_id: UUID, item_data: ItemUpdateSchema) -> ItemResponseSchema:
        logger.info(f"Editing item with ID: {item_id}")

        item_data_dict = item_data.dict(exclude_unset=True)  
        item = await self.item_service.get_item_by_id(item_id)
        if not item:
            raise ValueError("Item not found!")

        if item_data.discount_active:
            if item_data.discount_percent is None:
                raise ValueError("Discount percent is required when discount is active.")

            discount_percent = Decimal(str(item_data.discount_percent))
            discount_price = item.price * (Decimal("1") - discount_percent / Decimal("100"))
            
            item_data_dict["discount_price"] = discount_price
        else:
            item_data_dict["discount_percent"] = None
            item_data_dict["discount_expires_at"] = None
            item_data_dict["discount_price"] = None

        for key, value in item_data_dict.items():
            setattr(item, key, value)
            
        updated_item = await self.item_service.edit_item(item_id, item_data_dict)

        return ItemResponseSchema(
            item_id=updated_item.item_id,
            website_id=updated_item.website_id,
            category_id=updated_item.category_id,
            subcategory_id=updated_item.subcategory_id,
            name=updated_item.name,
            description=updated_item.description,
            price=updated_item.price,
            discount_price=discount_price,
            discount_active=updated_item.discount_active,
            discount_percent=updated_item.discount_percent,
            discount_expires_at=updated_item.discount_expires_at,
            delivery_url=updated_item.delivery_url,
            post_purchase_note=updated_item.post_purchase_note,
            stock=updated_item.stock,
            is_available=updated_item.is_available,
            created_at=updated_item.created_at,
        )
    

    async def delete_item(self, item_id: UUID) -> MessageResponse:
        logger.info(f"Deleting item with ID: {item_id}")

        await self.item_service.delete_item(item_id)

        return {"message": f"Item deleted successfully."}
    


    async def get_newest_items(self, website_id: UUID, limit: int) -> List[ItemResponseWithNameSchema]:
        items = await self.item_service.get_newest_items(website_id, limit)
        result = []
        for item in items:
            category = await self.website_service.get_category_by_id(item.category_id)
            subcategory = await self.website_service.get_subcategory_by_id(item.subcategory_id)

            category_name = category.name if category else 'null'
            subcategory_name = subcategory.name if subcategory else 'null'

            result.append(ItemResponseWithNameSchema(
                item_id=item.item_id,
                website_id=item.website_id,
                category_id=item.category_id,
                subcategory_id=item.subcategory_id,
                category_name=category_name,
                subcategory_name=subcategory_name,
                name=item.name,
                description=item.description,
                price=item.price,
                discount_price=item.discount_price,
                discount_percent= item.discount_percent,
                discount_active=item.discount_active,
                discount_expires_at=item.discount_expires_at,
                delivery_url=item.delivery_url,
                post_purchase_note=item.post_purchase_note,
                stock=item.stock,
                is_available=item.is_available,
                created_at=item.created_at,
            ))

        return result

    async def get_items_count(self, website_id: UUID) -> int:
        return await self.item_service.get_items_count(website_id)


    async def get_item_count_by_category_id(self, category_id: UUID) -> int:
        return await self.item_service.get_item_count_by_category_id(category_id)