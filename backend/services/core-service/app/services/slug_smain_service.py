from domain.schemas.review_schema import  ReviewResponseSchema
from services.slug_service import SlugService
from fastapi import HTTPException, Depends
from typing import Annotated, Optional
from uuid import UUID
from services.website_service import WebsiteService
class SlugMainService:
    def __init__(self, slug_service: Annotated[SlugService, Depends()],
        website_service: Annotated[WebsiteService, Depends()],):
        self.slug_service = slug_service
        self.website_service = website_service

    async def create_slug(self, slug: str, website_id: UUID) -> bool:
        exist_slug = await self.slug_service.get_slug(slug)
        if exist_slug:
            raise HTTPException(status_code=403, detail="Slug already exists.")
        return await self.slug_service.create_slug(slug, website_id)

    async def get_website_id(self, slug: str) -> Optional[int]:
        slug = await self.slug_service.get_slug(slug)
        if not slug: 
            raise HTTPException(status_code=404, detail="Slug Not Found.")
        return slug.website_id

    async def get_slug_by_website_id(self, website_id: UUID) -> Optional[str]:
        slug = await self.slug_service.get_slug_by_website_id(website_id)
        return slug.slug
    
    async def update_slug(self, website_id: UUID, new_slug: str) -> None:
        existing = await self.slug_service.get_slug(new_slug)
        if existing and existing.website_id != website_id:
            raise HTTPException(status_code=409, detail="Slug already in use by another website.")
        
        website = self.website_service.get_website_by_id(website_id)
        if not website:
            raise HTTPException(status_code=404, detail="Website not found.")

        await self.slug_service.update_slug(website_id, new_slug)
