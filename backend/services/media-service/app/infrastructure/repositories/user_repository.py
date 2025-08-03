from typing import Annotated, Dict
from loguru import logger
from fastapi import Depends
from sqlalchemy.orm import Session
from typing import Optional
from core.postgres_db.postgres_database import get_db
from domain.models.website_model import Website, WebsiteOwner
from domain.models.user_model import User  
from uuid import UUID

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