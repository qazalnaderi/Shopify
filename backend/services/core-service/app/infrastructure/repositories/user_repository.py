from typing import Annotated, Dict
from loguru import logger
from fastapi import Depends
from sqlalchemy.orm import Session
from typing import Optional
from core.postgres_db.database import get_db
from domain.models.website_model import User, Website, WebsiteOwner
from uuid import UUID
from sqlalchemy import func

class UserRepository:
  def __init__(self, db: Annotated[Session, Depends(get_db)]):
    self.db = db


  def get_user_by_email(self, email: str) -> User:
    logger.info(f"📥Fetching user with email: {email}")
    return self.db.query(User).filter(User.email == email).first()


  def get_user_by_id(self, user_id: UUID) -> User:
    logger.info(f"📥 Fetching user with id: {user_id}")
    return self.db.query(User).filter(User.user_id == user_id).first()

  def get_website_by_user_id(self, user_id: UUID) -> Optional[Website]:
    logger.info(f"Searching website for user_id: {user_id}")
    website_owner = self.db.query(WebsiteOwner).filter(WebsiteOwner.user_id == user_id).first()
    if not website_owner:
      return None
    website = self.db.query(Website).filter(Website.website_id == website_owner.website_id).first()
    return website
  
  def get_user_and_seller_counts(self):
    user_count = self.db.query(func.count()).select_from(User).scalar()

    seller_count = (
        self.db.query(func.count(func.distinct(WebsiteOwner.id)))
        .filter(WebsiteOwner.id.isnot(None))
        .scalar()
    )
    return {"total_users": user_count, "total_sellers": seller_count}
  

  