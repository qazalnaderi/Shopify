from typing import Annotated, Dict
from loguru import logger
from fastapi import Depends
from sqlalchemy.orm import Session
from core.postgres_db.database import get_db
from domain.models.buyer_model import Buyer 
import uuid


class BuyerRepository:
    def __init__(self, db: Annotated[Session, Depends(get_db)]):
        self.db = db

    def create_buyer(self, buyer: Buyer) -> Buyer:
        self.db.add(buyer)
        self.db.commit()
        self.db.refresh(buyer)
        logger.info(f"✅ Buyer {buyer.buyer_id} created")
        return buyer

    def get_buyer_by_email(self, email: str, website_id: uuid.UUID) -> Buyer:
        logger.info(f"📥 Fetching buyer with email: {email} for website: {website_id}")
        return self.db.query(Buyer).filter(
            Buyer.email == email,
            Buyer.website_id == website_id
        ).first()


    def get_buyer_by_phone_number(self, phone_number: str) -> Buyer:
        logger.info(f"📥 Fetching buyer with phone number: {phone_number}")
        return self.db.query(Buyer).filter(Buyer.phone_number == phone_number).first()

    def get_buyer_by_id(self, buyer_id: uuid.UUID) -> Buyer:
        logger.info(f"📥 Fetching buyer with id: {buyer_id}")
        return self.db.query(Buyer).filter(Buyer.buyer_id == buyer_id).first()

    def update_buyer(self, buyer_id: uuid.UUID, updated_buyer: Dict) -> Buyer:
        buyer_query = self.db.query(Buyer).filter(Buyer.buyer_id == buyer_id)
        db_buyer = buyer_query.first()

        if db_buyer:
            buyer_query.update(updated_buyer, synchronize_session=False)
            self.db.commit()
            self.db.refresh(db_buyer)
            logger.info(f"✅ Buyer {buyer_id} updated")
            return db_buyer
        else:
            logger.warning(f"⚠️ Buyer {buyer_id} not found")
            return None
