from pydantic import BaseModel, HttpUrl, Field
from uuid import UUID
from typing import Optional, Dict, List
from datetime import datetime


class FAQSchema(BaseModel):
    question: str
    answer: str


class SocialLinksSchema(BaseModel):
    telegram: Optional[HttpUrl]
    instagram: Optional[HttpUrl]

class WebsiteCreateSchema(BaseModel):
    business_name: str
    welcome_text: Optional[str] = None
    guide_page: Optional[str] = None
    social_links: Optional[ SocialLinksSchema] = None
    faqs: Optional[List[FAQSchema]]  

    class Config:
        from_attributes = True   

class WebsiteUpdateSchema(BaseModel):
    website_id:UUID
    business_name: Optional[str] = None
    website_url: Optional[str] = None
    custom_domain: Optional[str] = None
    logo_url: Optional[str] = None
    banner_image: Optional[str] = None
    welcome_text: Optional[str] = None
    guide_page: Optional[str] = None
    social_links: Optional[SocialLinksSchema] = None
    faqs: Optional[List[FAQSchema]] = None

    class Config:
        from_attributes = True

class WebsiteResponseSchema(BaseModel):
    id: Optional[UUID] = None
    business_name: str
    welcome_text: Optional[str] = None
    guide_page: Optional[str] = None
    social_links: Optional[SocialLinksSchema] = None
    faqs: Optional[List[FAQSchema]] = None
    website_url: Optional[str] = None
    custom_domain: Optional[str] = None
    logo_url: Optional[str] = None
    banner_image: Optional[str] = None
    created_at: Optional[datetime] = None
    message: Optional[str] = None

    class Config:
        from_attributes = True


class WebsiteCategoryCreateSchema(BaseModel):
    website_id: UUID
    name: str

class WebsiteCategoryResponseSchema(BaseModel):
    id: UUID
    website_id: UUID
    name: str
    is_active:bool
    created_at: datetime

    class Config:
        from_attributes = True


class WebsiteSubcategoryCreateSchema(BaseModel):
    parent_category_id: UUID
    name: str

    class Config:
        from_attributes = True

class WebsiteSubcategoryResponseSchema(BaseModel):
    id: UUID
    parent_category_id: UUID
    name: str
    created_at: datetime
    is_active:bool


    class Config:
        from_attributes = True


class MessageResponse(BaseModel):
    message: str
        


class AddWebsiteOwnerSchema(BaseModel):
    email: str
    website_id: UUID


class CategoryUpdateSchema(BaseModel):
    website_id: UUID
    category_id: UUID
    name: Optional[str]

    class Config:
        from_attributes = True

class SubCategoryUpdateSchema(BaseModel):
    website_id: UUID
    subcategory_id: UUID
    name: Optional[str]

    class Config:
        from_attributes = True

class CategoryResponseSchema(BaseModel):
    category_id: UUID
    name: str
    is_active: bool

    class Config:
        from_attributes = True

class SubCategoryResponseSchema(BaseModel):
    subcategory_id: UUID
    name: str
    is_active: bool

    class Config:
        from_attributes = True