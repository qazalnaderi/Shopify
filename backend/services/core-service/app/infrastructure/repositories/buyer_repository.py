from typing import Annotated, Dict, List
from loguru import logger
from fastapi import Depends
from sqlalchemy.orm import Session
from core.postgres_db.database import get_db
from domain.models.buyer_model import Buyer 
from uuid import UUID


class BuyerRepository:
    def __init__(self, db: Annotated[Session, Depends(get_db)]):
        self.db = db

    def create_buyer(self, buyer: Buyer) -> Buyer:
        self.db.add(buyer)
        self.db.commit()
        self.db.refresh(buyer)
        logger.info(f"✅ Buyer {buyer.buyer_id} created")
        return buyer

    def get_buyer_by_email(self, email: str) -> Buyer:
        logger.info(f"📥 Fetching buyer with email: {email}")
        return self.db.query(Buyer).filter(Buyer.email == email).first()

    def get_buyer_by_phone_number(self, phone_number: str) -> Buyer:
        logger.info(f"📥 Fetching buyer with phone number: {phone_number}")
        return self.db.query(Buyer).filter(Buyer.phone_number == phone_number).first()

    def get_buyer_by_id(self, buyer_id: UUID) -> Buyer:
        logger.info(f"📥 Fetching buyer with id: {buyer_id}")
        return self.db.query(Buyer).filter(Buyer.buyer_id == buyer_id).first()

    def update_buyer(self, buyer_id: UUID, updated_buyer: Dict) -> Buyer:
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


    # def get_buyers_by_website_id(self, website_id: UUID) -> List[Buyer]:
    #     buyers =  self.db.query(Buyer).filter(Buyer.website_id == website_id).all()
    #     if not buyers:
    #         logger.warning(f"⚠️ No Buyer found for website {website_id}")
    #         return None
    #     return buyers
    
    def get_buyers_count_by_website_id(self, website_id: UUID) -> int:
        return self.db.query(Buyer).filter(Buyer.website_id == website_id).count()