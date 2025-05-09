from schemas import TradeCreate
from db.crud import buy_crypto, sell_crypto, get_binance_price
from sqlalchemy.ext.asyncio import AsyncSession


TARGET_BUY_PRICE = 102_000
TARGET_SELL_PRICE = 103_646
TRADE_QUANTITY = 0.001


async def simple_buy_strategy(db: AsyncSession, user_id: str, symbol: str):
    current_price = await get_binance_price(symbol)
    if current_price < TARGET_BUY_PRICE:
        trade_data = TradeCreate(
            user_id=user_id,
            symbol=symbol,
            quantity=TRADE_QUANTITY,
            price=current_price
        )
        result = await buy_crypto(db, trade_data)
        return {
            "action": "buy",
            "executed": True,
            "price": current_price,
            "details": result
        }
    return {
        "action": "buy",
        "executed": False,
        "price": current_price,
        "message": f"Price {current_price} is not below target {TARGET_BUY_PRICE}"
    }


async def simple_sell_strategy(db: AsyncSession, user_id: str, symbol: str):
    current_price = await get_binance_price(symbol)
    if current_price > TARGET_SELL_PRICE:
        trade_data = TradeCreate(
            user_id=user_id,
            symbol=symbol,
            quantity=TRADE_QUANTITY,
            price=current_price
        )
        result = await sell_crypto(trade_data, db)
        return {
            "action": "sell",
            "executed": True,
            "price": current_price,
            "details": result
        }
    return {
        "action": "sell",
        "executed": False,
        "price": current_price,
        "message": f"Price {current_price} is not above target {TARGET_SELL_PRICE}"
    }
