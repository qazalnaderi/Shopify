from typing import Annotated
from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.core.postgres_db.database import get_db
from uuid import UUID
from app.domain.models.order_model import Order, OrderItem
from app.domain.models.website_model import Item
from app.infrastructure.repositories.item_repository import ItemRepository
from app.infrastructure.repositories.cart_repository import CartRepository
from datetime import datetime
from datetime import date
from sqlalchemy import extract, func
from app.utils.date_utils import to_jalali_str

class OrderRepository:
    def __init__(self,
    db: Annotated[Session, Depends(get_db)],
    item_repository: Annotated[ItemRepository, Depends()],
    cart_repository: Annotated[CartRepository, Depends()],
    ):
      self.db = db
      self.item_repository = item_repository
      self.cart_repository = cart_repository

        
    def create_order_from_cart(self, buyer_id: UUID, website_id: UUID) -> Order:
        cart_items = self.cart_repository.get_cart_items_by_buyer(buyer_id)
        if not cart_items:
            raise HTTPException(status_code=404, detail="Cart is empty for this website.")

        total_price = 0
        for cart_item in cart_items:
            item = self.item_repository.get_item_by_id(cart_item.item_id)
            price = item.discount_price if (item.discount_active and item.discount_expires_at and item.discount_expires_at > datetime.utcnow()) else item.price
            total_price += float(price) * cart_item.quantity

        order = Order(
            website_id=website_id,
            buyer_id=buyer_id,
            status='Pending',
            total_price=total_price,
            created_at=datetime.utcnow()
        )
        self.db.add(order)
        self.db.flush()  

        for cart_item in cart_items:
            item = self.item_repository.get_item_by_id(cart_item.item_id)
            price = item.discount_price if (item.discount_active and item.discount_expires_at and item.discount_expires_at > datetime.utcnow()) else item.price

            order_item = OrderItem(
                order_id=order.order_id,
                item_id=cart_item.item_id,
                quantity=cart_item.quantity,
                price=price * cart_item.quantity
            )
            self.db.add(order_item)

        self.db.commit()
        return order


    def get_orders_by_buyer(self, buyer_id: UUID) -> List[Order]:
     return self.db.query(Order).filter(Order.buyer_id == buyer_id).all()
    

    def get_order_by_id(self, order_id: UUID) -> Order:
     return self.db.query(Order).filter(Order.order_id == order_id).first()

    def get_orders_by_website_id(self, website_id:UUID)-> List[Order]:
        return self.db.query(Order).filter(Order.website_id == website_id).all()
    

    def update_order_status(self, order_id: UUID, new_status: str) -> None:
        order = self.get_order_by_id(order_id)
        
        if order:
            order.status = new_status
            self.db.commit()
            self.db.refresh(order)  
        else:
            raise Exception(f"Order with ID {order_id} not found.")
        
    async def get_order_items(self, order_id: UUID):
        return self.db.query(OrderItem).filter(OrderItem.order_id == order_id).all()

    def get_pending_order(self, buyer_id: UUID) -> List[Order]:
        return self.db.query(Order).filter(Order.buyer_id == buyer_id, Order.status == "Pending").first()  


    def get_order_item_by_buyer_and_item(self, buyer_id:UUID, item_id:UUID)-> OrderItem:
        order_item = self.db.query(OrderItem).join(Order).filter(
            Order.buyer_id == buyer_id,         
            OrderItem.item_id == item_id,      
            Order.status == 'Paid'               
        ).first()   

        return order_item        
    

    def get_active_buyers_count_by_website(self, website_id: UUID) -> int:
        return self.db.query(func.count(func.distinct(Order.buyer_id))) \
            .filter(Order.website_id == website_id) \
            .filter(Order.status == 'Paid') \
            .scalar()
    

    def get_sales_by_day(self, website_id: UUID, day: date) -> dict:
        result = self.db.query(
            func.count(Order.order_id),
            func.coalesce(func.sum(Order.total_price), 0)
        ).filter(
            Order.website_id == website_id,
            func.date(Order.created_at) == day,
            Order.status == 'Paid'
        ).first()

        return {"count": result[0], "revenue": result[1]}

    def get_sales_by_month(self, website_id: UUID, year: int, month: int) -> dict:
        result = self.db.query(
            func.count(Order.order_id),
            func.coalesce(func.sum(Order.total_price), 0)
        ).filter(
            Order.website_id == website_id,
            extract("year", Order.created_at) == year,
            extract("month", Order.created_at) == month,
            Order.status == 'Paid'
        ).first()

        return {"count": result[0], "revenue": result[1]}

    def get_sales_by_year(self, website_id: UUID, year: int) -> dict:
        result = self.db.query(
            func.count(Order.order_id),
            func.coalesce(func.sum(Order.total_price), 0)
        ).filter(
            Order.website_id == website_id,
            extract("year", Order.created_at) == year,
            Order.status == 'Paid'
        ).first()

        return {"count": result[0], "revenue": result[1]}
    

    def get_total_revenue_for_month(self, website_id: UUID, year: int, month: int) -> int:
        result = self.db.query(
            func.coalesce(func.sum(Order.total_price), 0)
        ).filter(
            Order.website_id == website_id,
            extract("year", Order.created_at) == year,
            extract("month", Order.created_at) == month,
            Order.status == 'Paid'
        ).scalar()

        return result or 0
    

    def get_total_revenue(self, website_id: UUID) -> dict:
        total = self.db.query(func.sum(Order.total_price)) \
            .filter(Order.website_id == website_id, Order.status == 'Paid') \
            .scalar() or 0

        return {"total_revenue": total}

    def get_total_sales_count(self, website_id: UUID) -> int:
        count = self.db.query(func.count(Order.order_id)).filter(
            Order.website_id == website_id,
            Order.status == 'Paid'
        ).scalar() or 0
        return count


    def get_latest_orders(self, website_id: UUID, limit: int = 5) -> list:
        orders = self.db.query(Order).filter(
            Order.website_id == website_id,
            Order.status == 'Paid'
        ).order_by(Order.created_at.desc()).limit(limit).all()

        result = []

        for order in orders:
            order_items = self.db.query(OrderItem).filter(OrderItem.order_id == order.order_id).all()
            for order_item in order_items:
                item_obj = self.db.query(Item).filter(Item.item_id == order_item.item_id).first()
                if item_obj:
                    result.append({
                        "item_name": item_obj.name,         
                        "amount": order_item.price,             
                        "date": to_jalali_str(order.created_at)
                    })
        return result

    def get_best_selling_items(self, website_id: UUID, limit: int = 5) -> list:
        from sqlalchemy import func
        results = self.db.query(
            Item.name,
            func.sum(OrderItem.price).label("total_amount"),
            func.count(OrderItem.item_id).label("sales_count")
        ).join(
            OrderItem, OrderItem.item_id == Item.item_id
        ).join(
            Order, Order.order_id == OrderItem.order_id
        ).filter(
            Order.website_id == website_id,
            Order.status == 'Paid'
        ).group_by(Item.item_id, Item.name
        ).order_by(func.count(OrderItem.item_id).desc()
        ).limit(limit).all()

        return [
            {
                "product_name": result.name,
                "total_amount": result.total_amount,
                "sales_count": result.sales_count
            }
            for result in results
        ]


    def get_average_order_per_buyer(self, website_id: UUID, buyers_count: int) -> int:
        total = self.db.query(func.sum(Order.total_price)).filter(
            Order.website_id == website_id,
            Order.status == 'Paid'
        ).scalar() or 0

        if buyers_count == 0:
            return 0

        return int(total / buyers_count)
