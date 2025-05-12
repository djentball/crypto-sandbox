from sqlalchemy import Column, String, Float, ForeignKey, DateTime, Enum
from sqlalchemy.orm import relationship
import datetime
import uuid
import enum
from db.db import Base


def generate_uuid():
    return str(uuid.uuid4())

class Price(Base):
    __tablename__ = "prices"

    id = Column(String, primary_key=True, default=generate_uuid)
    symbol = Column(String, index=True)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow, index=True)
    open = Column(Float)
    high = Column(Float)
    low = Column(Float)
    close = Column(Float)
    volume = Column(Float)

class TradeType(str, enum.Enum):
    buy = "buy"
    sell = "sell"

class Trade(Base):
    __tablename__ = "trades"

    id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, ForeignKey('users.id'))
    symbol = Column(String, index=True)
    type = Column(Enum(TradeType), nullable=False)
    price = Column(Float, nullable=False)
    quantity = Column(Float, nullable=False)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    user = relationship("User", back_populates="trades")

class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=generate_uuid)
    name = Column(String, unique=True, index=True)
    usd_balance = Column(Float, default=1000.0)
    wallets = relationship("Wallet", back_populates="user")
    trades = relationship("Trade", back_populates="user")


class Wallet(Base):
    __tablename__ = "wallets"

    id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, ForeignKey("users.id"))
    symbol = Column(String)
    amount = Column(Float, default=0.0)

    user = relationship("User", back_populates="wallets")


class BasePrice(Base):
    __tablename__ = "base_price"

    symbol = Column(String, primary_key=True)
    price = Column(Float, nullable=False)