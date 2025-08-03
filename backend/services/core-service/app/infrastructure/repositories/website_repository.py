from domain.models.website_model import Website, WebsiteOwner, WebsiteCategory, WebsiteSubcategory, Announcement, User
from domain.models.buyer_model import Buyer
from sqlalchemy.orm import Session
from loguru import logger
from uuid import UUID
from core.postgres_db.database import get_db
from typing import Annotated
from fastapi import Depends
from typing import List, Optional
from sqlalchemy import func
from utils.date_utils import to_jalali_str


class WebsiteRepository:
    def __init__(self, db: Annotated[Session, Depends(get_db)]):
        self.db = db
        
    def create_website(self, website: Website) -> Website:
        self.db.add(website)
        self.db.commit()
        self.db.refresh(website)
        logger.info(f"✅ Website created with id: {website.website_id}")
        return website

    def create_website_owner(self, user_id: UUID, website_id: UUID) -> WebsiteOwner:
        website_owner = WebsiteOwner(user_id=user_id, website_id=website_id)
        self.db.add(website_owner)
        self.db.commit()
        self.db.refresh(website_owner)
        logger.info(f"✅ website owner with user_id {user_id} associated with website {website_id}")
        return website_owner

    def create_website_category(self, website_category: WebsiteCategory) -> WebsiteCategory:
        self.db.add(website_category)
        self.db.commit()
        self.db.refresh(website_category)
        logger.info(f"✅ website category '{website_category.name}' created with id: {website_category.id}")
        return website_category    


    def get_website_by_id(self, website_id: UUID) -> Website:
        website = self.db.query(Website).filter(Website.website_id == website_id).first()

        if not website :
            logger.warning(f"⚠️ No website found with id: {website_id}")
        else:
            logger.info(f"✅ Website found with id: {website_id}")

        return website   

    def create_website_subcategory(self, subcategory: WebsiteSubcategory) -> WebsiteSubcategory:
        self.db.add(subcategory)
        self.db.commit()
        self.db.refresh(subcategory)
        logger.info(f"✅ Subcategory '{subcategory.name}' created with id: {subcategory.id}")
        return subcategory    


    def get_website_categories_by_website_id(self, website_id: UUID) -> List[WebsiteCategory]:
        categories = self.db.query(WebsiteCategory).filter(WebsiteCategory.website_id == website_id).all()
        return categories    

    def get_category_by_id(self, category_id: UUID) -> WebsiteCategory:
        category = self.db.query(WebsiteCategory).filter(WebsiteCategory.id == category_id).first()
        
        if not category :
            logger.warning(f"⚠️ No category found with id: {category_id}")
        else:
            logger.info(f"✅ category found with id: {category_id}")
    
        return category
    
    def get_subcategory_by_id(self, subcategory_id: UUID) -> WebsiteCategory:
        subcategory = self.db.query(WebsiteSubcategory).filter(WebsiteSubcategory.id == subcategory_id).first()
        return subcategory
    

    def delete_category(self, category_id: UUID) -> None:
        self.db.query(WebsiteCategory).filter(WebsiteCategory.id == category_id).update({WebsiteCategory.is_active: False})
        self.db.query(WebsiteSubcategory).filter(WebsiteSubcategory.parent_category_id == category_id).update({WebsiteSubcategory.is_active: False})
        self.db.commit()
        logger.info(f"✅ Deleted category with ID {category_id} from database.")


    def delete_subcategory(self, subcategory_id: UUID) -> None:
        self.db.query(WebsiteSubcategory).filter(WebsiteSubcategory.id == subcategory_id).update({WebsiteSubcategory.is_active: False})
        self.db.commit()
        logger.info(f"✅ Deleted subcategory with ID {subcategory_id} from database.")    
       
    # def get_website_by_name(self, website_name: str) -> Website:
    #     website = self.db.query(Website).filter(Website.custom_domain == website_name).first()
    #     return website
    
    def get_subcategories_by_category_id(self, category_id: UUID) -> List[WebsiteSubcategory]:
        return self.db.query(WebsiteSubcategory).filter(WebsiteSubcategory.parent_category_id == category_id).all()
    


    def get_owner(self, user_id: UUID) -> Optional[WebsiteOwner]:
        return self.db.query(WebsiteOwner).filter(
            WebsiteOwner.user_id == user_id
        ).first()

    def get_owner_by_user_and_website(self, user_id: UUID, website_id: UUID) -> Optional[WebsiteOwner]:
        return self.db.query(WebsiteOwner).filter(
            WebsiteOwner.user_id == user_id,
            WebsiteOwner.website_id == website_id
        ).first()

    def update_category(self, category: WebsiteCategory) -> None:
        self.db.add(category)
        self.db.commit()
        self.db.refresh(category)
        logger.info(f"✅ Category with ID {category.id} successfully updated in the database.")

    def update_subcategory(self, subcategory: WebsiteSubcategory) -> None:
        self.db.add(subcategory)
        self.db.commit()
        self.db.refresh(subcategory)
        logger.info(f"✅ Subcategory with ID {subcategory.id} successfully updated in the database.") 

    def update_website(self,website: Website) -> Website:

        updated_website = self.get_website_by_id(website.website_id)
        self.db.add(website)
        self.db.commit()
        self.db.refresh(website)
        logger.info(f"✅ website with ID {website.website_id} successfully updated in the database.")   
        return updated_website        
    
    def get_total_buyers_count(self, website_id: UUID) -> int:
        count = self.db.query(func.count(Buyer.buyer_id)).filter(
            Buyer.website_id == website_id
        ).scalar() or 0
        return count


    def get_latest_announcements(self, website_id: UUID) -> list:
        announcements = self.db.query(Announcement).filter(
            Announcement.website_id == website_id
        ).order_by(Announcement.created_at.desc()).all()

        return [
            {
                "text": a.message,
                "date": to_jalali_str(a.created_at),
            }
            for a in announcements
        ]


    def get_website_owner_email(self, website_id: UUID) -> Optional[str]:
        
        result = (
            self.db.query(User.email)
            .join(WebsiteOwner, WebsiteOwner.user_id == User.user_id)
            .filter(WebsiteOwner.website_id == website_id)
            .first()
        )
        return result[0] if result else None
    

    def get_all_websites(self) -> list[Website]:
        return (
            self.db.query(Website)
            .order_by(Website.created_at.desc())  
            .all()
        )
