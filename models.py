from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__="users"
    id=Column(Integer, primary_key=True, index=True)
    username=Column(String)
    telegram_id=Column(Integer)
    token=Column(String)
    pubkey=Column(String)

class Message(Base):
    __tablename__="messages"
    id=Column(Integer, primary_key=True, index=True)
    from_id=Column(Integer)
    to_id=Column(Integer)
    iv=Column(String)
    ciphertext=Column(String)
    msg_type=Column(String)
    ttl_sec=Column(Integer)
    created_at=Column(DateTime, default=datetime.utcnow)