import httpx
from datetime import datetime, UTC
from uuid import uuid4
from typing import Sequence, Optional

from fastapi import Depends, HTTPException
from sqlalchemy import select, exists, desc
from sqlalchemy.ext.asyncio import AsyncSession

from db.models import Price, Trade, Wallet, User, TradeType, BasePrice
from schemas import (
    PriceCreate,
    WalletCreate,
    UserCreate,
    TradeCreate,
    TradeOut,
    UserBalanceOut,
    CryptoBalance,
)

from db.db import get_db


async def add_price(session: AsyncSession, price: PriceCreate) -> Price:
    db_price = Price(**price.dict())
    session.add(db_price)
    await session.commit()
    await session.refresh(db_price)
    return db_price


# Перевірити, чи свічка вже є (щоб не дублювати по timestamp + symbol)
async def price_exists(session: AsyncSession, symbol: str, timestamp: datetime) -> bool:
    result = await session.execute(
        select(exists().where(Price.symbol == symbol, Price.timestamp == timestamp))
    )
    return result.scalar()


# Отримати останні N записів для символу
async def get_prices(session: AsyncSession, symbol: str, limit: int = 100) -> Sequence[Price]:
    result = await session.execute(
        select(Price)
        .where(Price.symbol == symbol)
        .order_by(Price.timestamp.desc())
        .limit(limit)
    )
    return result.scalars().all()


# Отримати історію угод (опціонально по символу)
async def get_trades(session: AsyncSession, symbol: str = None, limit: int = 100) -> Sequence[Trade]:
    stmt = select(Trade).order_by(Trade.timestamp.desc()).limit(limit)
    if symbol:
        stmt = stmt.where(Trade.symbol == symbol)
    result = await session.execute(stmt)
    return result.scalars().all()


# ===== USERS =====

async def create_user(session: AsyncSession, user: UserCreate) -> User:
    db_user = User(name=user.name)
    session.add(db_user)
    await session.commit()
    await session.refresh(db_user)
    return db_user


async def get_user_by_name(session: AsyncSession, name: str) -> Optional[User]:
    result = await session.execute(select(User).where(User.name == name))
    return result.scalars().first()


async def get_user_by_id(session: AsyncSession, user_id: str) -> Optional[User]:
    result = await session.execute(select(User).where(User.id == user_id))
    return result.scalars().first()


# ===== WALLETS =====

async def get_wallet(session: AsyncSession, user_id: str, symbol: str) -> Optional[Wallet]:
    result = await session.execute(
        select(Wallet).where(Wallet.user_id == user_id, Wallet.symbol == symbol)
    )
    return result.scalars().first()


async def create_wallet(session: AsyncSession, wallet: WalletCreate) -> Wallet:
    db_wallet = Wallet(**wallet.dict())
    session.add(db_wallet)
    await session.commit()
    await session.refresh(db_wallet)
    return db_wallet


async def get_user_wallets(session: AsyncSession, user_id: str) -> Sequence[Wallet]:
    result = await session.execute(select(Wallet).where(Wallet.user_id == user_id))
    return result.scalars().all()


async def get_latest_price(session: AsyncSession, symbol: str):
    result = await session.execute(
        select(Price).where(Price.symbol == symbol).order_by(desc(Price.timestamp)).limit(1)
    )
    return result.scalars().first()


async def buy_crypto(db: AsyncSession, trade: TradeCreate):
    user = await get_user_by_id(db, trade.user_id)
    if not user:
        return {"error": "User not found"}

    try:
        # Отримуємо актуальну ціну з Binance
        current_price = await get_binance_price(trade.symbol)
    except Exception as e:
        return {"error": f"Failed to fetch price from Binance: {str(e)}"}

    trade.price = current_price
    total_cost = trade.price * trade.quantity

    if user.usd_balance < total_cost:
        return {
            "error": "Insufficient balance",
            "current_balance": user.usd_balance,
            "required": total_cost
        }

    user.usd_balance -= total_cost

    wallet = await get_wallet(db, trade.user_id, trade.symbol)
    if wallet:
        wallet.amount += trade.quantity
    else:
        wallet = Wallet(
            id=str(uuid4()),
            user_id=trade.user_id,
            symbol=trade.symbol,
            amount=trade.quantity
        )
        db.add(wallet)

    new_trade = Trade(
        id=str(uuid4()),
        user_id=trade.user_id,
        symbol=trade.symbol,
        price=trade.price,
        quantity=trade.quantity,
        timestamp=datetime.now(UTC),
        type="buy"
    )
    db.add(new_trade)
    await db.commit()
    await db.refresh(new_trade)

    return {
        "trade": new_trade,
        "total_cost": total_cost
    }


async def sell_crypto(trade: TradeCreate, db: AsyncSession):
    # Отримаємо актуальну ціну з Binance
    symbol = trade.symbol.upper()
    trade_price = await get_binance_price(symbol)
    trade.price = trade_price

    # Отримуємо користувача
    user = await get_user_by_id(db, trade.user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Отримуємо гаманець
    wallet = await get_wallet(db, trade.user_id, symbol)
    if not wallet or wallet.amount < trade.quantity:
        raise HTTPException(status_code=400, detail="Insufficient crypto balance")

    # Віднімаємо з гаманця
    wallet.amount -= trade.quantity
    db.add(wallet)

    # Додаємо до балансу користувача
    total_sale_value = trade.quantity * trade_price
    user.usd_balance += total_sale_value
    db.add(user)

    # Підрахунок прибутку (опційно)
    avg_buy_price = await get_average_buy_price(db, trade.user_id, symbol)
    profit = None
    if avg_buy_price is not None:
        profit = (trade_price - avg_buy_price) * trade.quantity

    # Створюємо запис про продаж
    new_trade = Trade(
        id=str(uuid4()),
        user_id=trade.user_id,
        symbol=symbol,
        type=TradeType.sell,
        price=trade_price,
        quantity=trade.quantity,
        timestamp=datetime.now(UTC)
    )
    db.add(new_trade)

    await db.commit()
    await db.refresh(new_trade)

    # Додаємо прибуток до об'єкта (але не в БД)
    new_trade.profit = profit
    return new_trade


async def get_binance_price(symbol: str) -> float:
    url = f"https://api.binance.com/api/v3/ticker/price?symbol={symbol}"
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        response.raise_for_status()
        data = response.json()
        return float(data["price"])


async def get_user_balance(db: AsyncSession, user_id: str) -> UserBalanceOut | None:
    user_result = await db.execute(select(User).where(User.id == user_id))
    user = user_result.scalars().first()
    if not user:
        return None

    wallets_result = await db.execute(select(Wallet).where(Wallet.user_id == user_id))
    wallets = wallets_result.scalars().all()

    total_crypto_value = 0.0
    crypto_details = {}

    for wallet in wallets:
        try:
            price = await get_binance_price(wallet.symbol)
        except Exception as e:

            price = 0.0

        value = wallet.amount * price
        total_crypto_value += value

        crypto_details[wallet.symbol] = CryptoBalance(
            amount=wallet.amount,
            price=round(price, 2),
            value_usd=round(value, 2)
        )

    total_balance = user.usd_balance + total_crypto_value

    return UserBalanceOut(
        usd_balance=round(user.usd_balance, 2),
        crypto=crypto_details,
        total_balance_usd=round(total_balance, 2)
    )


async def get_average_buy_price(db: AsyncSession, user_id: str, symbol: str) -> Optional[float]:
    result = await db.execute(
        select(Trade)
        .where(
            Trade.user_id == user_id,
            Trade.symbol == symbol,
            Trade.type == TradeType.buy
        )
    )
    trades = result.scalars().all()
    if not trades:
        return None

    total_quantity = sum(t.quantity for t in trades)
    total_spent = sum(t.price * t.quantity for t in trades)

    if total_quantity == 0:
        return 0.0

    return total_spent / total_quantity


async def set_base_price(session: AsyncSession, symbol: str, price: float) -> BasePrice:
    db_price = await session.get(BasePrice, symbol)
    if db_price:
        db_price.price = price
    else:
        db_price = BasePrice(symbol=symbol, price=price)
        session.add(db_price)
    await session.commit()
    return db_price


async def get_base_price(session: AsyncSession, symbol: str) -> float:
    db_price = await session.get(BasePrice, symbol)
    if db_price:
        return db_price.price
    raise HTTPException(status_code=404, detail=f"Base price for {symbol} not found")
