from databases import DatabaseURL
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy_utils import database_exists, create_database
from loguru import logger
from core.config.config import get_settings

config = get_settings()
# DATABASE_URL = "postgresql://postgres:admin@postgres_container:5432/shopify"
# DATABASE_URL = "postgresql://postgres:admin@localhost:5432/shopify"
DATABASE_URL = "postgresql://root:gQoaHut2yzfadEWP85RofClM@shopify:5432/postgres"

# DATABASE_URL = (
#     f"{config.DATABASE_DIALECT}://"
#     f"{config.DATABASE_USERNAME}:"
#     f"{config.DATABASE_PASSWORD}@"
#     f"{config.DATABASE_HOSTNAME}:"
#     f"{config.DATABASE_PORT}/"
#     f"{config.DATABASE_NAME}"
# )
engine = create_engine(DATABASE_URL, future=True)
session_local = sessionmaker(autoflush=False, autocommit=False, bind=engine)

Base = declarative_base()


def init_db() -> bool:
    Base.metadata.create_all(bind=engine)
    logger.info("Database Initialized")
    return True


def get_db():
    db = session_local()
    try:
        yield db
    finally:
        db.close()
