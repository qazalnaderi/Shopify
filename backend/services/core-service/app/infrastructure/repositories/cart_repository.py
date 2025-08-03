from sqlalchemy.orm import Session
from domain.models.buyer_model import CartItem
from core.postgres_db.database import get_db
from fastapi import Depends
from uuid import UUID
import datetime
from loguru import logger
from typing import List, Optional,Annotated
from fastapi import HTTPException


class CartRepository:
  def __init__(self, db: Annotated[Session, Depends(get_db)]):
    self.db = db

  def add_item(self, website_id: UUID, buyer_id: UUID, item_id: UUID, stock: int) -> CartItem:
    existing_cart_item = self.db.query(CartItem).filter_by(
        website_id=website_id,
        buyer_id=buyer_id,
        item_id=item_id).first()
    
    now = datetime.datetime.utcnow()
    expires_at = now + datetime.timedelta(hours=2)

    if stock <= 0:
        logger.info(f"Item {item_id} is out of stock")
        raise HTTPException(status_code=400, detail="Item is out of stock")

    if existing_cart_item:
        if existing_cart_item.quantity < stock:
            existing_cart_item.quantity += 1 
            existing_cart_item.expires_at = expires_at
            self.db.commit()
            self.db.refresh(existing_cart_item)
            logger.info(f"Updated quantity of item {item_id} in cart for buyer {buyer_id}")
            return existing_cart_item
        else:
            logger.info(f"Not enough stock to add more of item {item_id}")
            raise HTTPException(status_code=400, detail="Not enough stock")

    else:
        if stock < 1:
            logger.info(f"Not enough stock to add item {item_id} to cart for buyer {buyer_id}")
            raise HTTPException(status_code=400, detail="Not enough stock to add item")

        # Add the item to the cart
        cart_item = CartItem(
            website_id=website_id,
            buyer_id=buyer_id,
            item_id=item_id,
            quantity=1,  # Default quantity is 1
            added_at=now,
            expires_at=expires_at
        )
        self.db.add(cart_item)
        self.db.commit()
        self.db.refresh(cart_item)
        logger.info(f"Added item {item_id} to cart for buyer {buyer_id}")
        return cart_item

    

  def get_cart_items_by_buyer(self, buyer_id: UUID) -> List[CartItem]:
    return self.db.query(CartItem).filter(CartItem.buyer_id == buyer_id).all()   
  

  def delete_expired_items(self, current_time: datetime):
    expired_items = self.db.query(CartItem).filter(CartItem.expires_at <= current_time).all()
    for item in expired_items:
        self.db.delete(item)
    self.db.commit()
    self.db.close()

  def remove_one_from_cart(self, cart_item_id: UUID):
    cart_item = self.db.query(CartItem).filter(CartItem.id == cart_item_id).first()
    if not cart_item:
      raise Exception("Cart item not found")

    if cart_item.quantity > 1:
      cart_item.quantity -= 1
      self.db.commit()
      self.db.refresh(cart_item)
      return cart_item
    else:
      self.db.delete(cart_item)
      self.db.commit()
      return None


  def get_cart_item(self, cart_item_id: UUID) -> Optional[CartItem]:
    return self.db.query(CartItem).filter(CartItem.id == cart_item_id).first()

  def delete_cart_item(self, cart_item_id: UUID) -> bool:
    cart_item = self.get_cart_item(cart_item_id)
    if not cart_item:
      return False
    self.db.delete(cart_item)
    self.db.commit()
    logger.info(f"Cart item {cart_item_id} deleted from cart")
    return True
  

  def clear_cart(self, buyer_id: UUID):
    self.db.query(CartItem).filter_by(buyer_id=buyer_id).delete()
    self.db.commit()
