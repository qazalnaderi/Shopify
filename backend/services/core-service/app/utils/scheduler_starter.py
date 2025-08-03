from core.postgres_db.database import get_db
from infrastructure.repositories.cart_repository import CartRepository
from infrastructure.repositories.plan_repository import PlanRepository
from infrastructure.repositories.order_repository import OrderRepository
from infrastructure.repositories.item_repository import ItemRepository
from infrastructure.scheduler.scheduler import SchedulerService

def starter():
    db = next(get_db()) 
    plan_repo = PlanRepository(db)
    cart_repo = CartRepository(db)
    item_repo =ItemRepository(db)
    order_repo = OrderRepository(db,cart_repo,item_repo)
    check_plan_scheduler = SchedulerService(plan_repo,cart_repo,order_repo)
    check_plan_scheduler.start()