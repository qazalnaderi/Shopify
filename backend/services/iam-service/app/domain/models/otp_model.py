from sqlalchemy import Column, String, Text, TIMESTAMP, func, Boolean, ForeignKey, BigInteger
from sqlalchemy.dialects.postgresql import UUID
import uuid
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import JSONB
import datetime

Base = declarative_base()
class OTP(Base):
    __tablename__ = 'otp'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    email = Column(String(255), nullable=False)
    otp = Column(BigInteger, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.current_timestamp())
    expires_at = Column(TIMESTAMP)
