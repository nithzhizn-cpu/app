from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from app.database import Base

class User(Base):
    tablename = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    telegram_id = Column(String, nullable=True)
    token = Column(String, unique=True)
    pubkey = Column(String, nullable=True)

class Message(Base):
    tablename = "messages"

    id = Column(Integer, primary_key=True)
    from_id = Column(Integer, nullable=False)
    to_id = Column(Integer, nullable=False)
    iv = Column(String, nullable=False)
    ciphertext = Column(String, nullable=False)
    msg_type = Column(String, nullable=True)
    ttl_sec = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
