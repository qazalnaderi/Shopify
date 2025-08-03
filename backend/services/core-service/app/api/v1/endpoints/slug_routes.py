from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from services.slug_smain_service import SlugMainService
from domain.schemas.slug_schema import CreateSlugInput
from typing import Annotated

slug_router = APIRouter()



@slug_router.post("/slug")
async def create_slug(new_slug: CreateSlugInput, service: Annotated[SlugMainService, Depends()]):
    await service.create_slug(new_slug.slug, new_slug.website_id)
    return {"slug": new_slug.slug, "website_id": new_slug.website_id}


@slug_router.get("/slug/{slug}")
async def get_slug(slug: str, service: Annotated[SlugMainService, Depends()]):
    website_id = await service.get_website_id(slug)
    return {"website_id": website_id}


@slug_router.get("/get-slug-by/{website_id}")
async def get_slug_by_website_id(website_id: UUID, service: Annotated[SlugMainService, Depends()]):
    return await service.get_slug_by_website_id(website_id)

@slug_router.put("/update-slug", status_code=status.HTTP_200_OK)
async def update_slug(
website_id: UUID,
service: Annotated[SlugMainService, Depends()],
new_slug: str
):
    await service.update_slug(website_id, new_slug)
    return {"detail":"updated successfully"}