from typing import Annotated, Dict
from loguru import logger
from fastapi import Depends, HTTPException
from typing import Optional
from app.infrastructure.repositories.slug_repository import SlugRepository
from app.services.base_service import BaseService
from app.domain.models.slug_model import SlugModel
from uuid import UUID

class SlugService:
    def __init__(self, slug_repo:Annotated[SlugRepository, Depends()],):
        self.slug_repo = slug_repo

    async def create_slug(self, slug: str, website_id: UUID) -> bool:
        slug = SlugModel(
            website_id= website_id,
            slug=slug
        )
        return self.slug_repo.create(slug)

    async def get_slug(self, slug: str) -> Optional[UUID]:
        return self.slug_repo.get_slug(slug)

    async def get_slug_by_website_id(self, website_id: UUID) -> Optional[UUID]:
        return self.slug_repo.get_slug_by_website_id(website_id)