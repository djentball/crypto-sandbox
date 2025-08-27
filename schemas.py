from typing import Optional, Dict
from pydantic import BaseModel
from datetime import datetime
from enum import Enum


class TradeType(str, Enum):
    buy = "buy"
    sell = "sell"


class TradeBase(BaseModel):
    user_id: str
    symbol: str
    quantity: float


class TradeCreate(TradeBase):
    type: Optional[TradeType] = None
    price: Optional[float] = None


class TradeResponse(BaseModel):
    message: str


class TradeOut(TradeBase):
    id: str
    timestamp: datetime
    type: TradeType
    profit: Optional[float] = None
    total_cost: Optional[float] = None

    class Config:
        from_attributes = True


class PriceBase(BaseModel):
    symbol: str
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float


class PriceCreate(PriceBase):
    pass


class PriceOut(PriceCreate):
    id: str


class Price(PriceBase):
    class Config:
        from_attributes = True


class UserBase(BaseModel):
    name: str


class UserCreate(UserBase):
    pass

class User(UserBase):
    id: str
    usd_balance: float

    class Config:
        from_attributes = True


class WalletBase(BaseModel):
    symbol: str
    amount: float


class WalletCreate(WalletBase):
    user_id: str


class Wallet(WalletBase):
    id: str
    user_id: str

    class Config:
        from_attributes = True


class CryptoBalance(BaseModel):
    amount: float
    price: float
    value_usd: float


class UserBalanceOut(BaseModel):
    usd_balance: float
    crypto: Dict[str, CryptoBalance]
    total_balance_usd: float


class BasePriceUpdate(BaseModel):
    symbol: str
    price: float


class FuturesPositionCreate(BaseModel):
    symbol: str
    quantity: float
    leverage: int = 1
    side: str  # LONG/SHORT
    take_profit_price: float | None = None


class FuturesPositionOut(FuturesPositionCreate):
    id: str
    entry_price: float
    mark_price: float
    liquidation_price: float
    pnl: float
    timestamp: datetime
