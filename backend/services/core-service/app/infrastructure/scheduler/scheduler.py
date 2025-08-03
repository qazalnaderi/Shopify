from infrastructure.repositories.cart_repository import CartRepository
from infrastructure.repositories.plan_repository import PlanRepository
from infrastructure.repositories.order_repository import OrderRepository
from loguru import logger
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime

class SchedulerService:
    def __init__(self, plan_repository: PlanRepository,cart_repository: CartRepository ,order_repository: OrderRepository):
        self.scheduler = BackgroundScheduler()
        self.plan_repository = plan_repository
        self.cart_repository = cart_repository
        self.order_repository = order_repository

    def start(self):
        logger.info("🔄 Starting background job scheduler...")
        self.scheduler.add_job(self.deactivate_expired_plans, 'interval', hours=24) 
        self.scheduler.add_job(self.cleanup_expired_items, 'interval', minutes = 30)
        self.scheduler.add_job(self.cleanup_pending_orders, 'interval', minutes = 30)

        self.scheduler.start()

    def deactivate_expired_plans(self):
        self.plan_repository.deactivate_expired_plans()

    def cleanup_expired_items(self):
        now = datetime.utcnow()
        self.cart_repository.delete_expired_items(now)
        logger.info("Expired cart items cleaned up.")

    def cleanup_pending_orders(self):
        now = datetime.utcnow()
        self.order_repository.delete_expired_pending_orders(now)
        logger.info("Expired pending orders cleaned up.")
