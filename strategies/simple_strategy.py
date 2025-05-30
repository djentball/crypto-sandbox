from schemas import TradeCreate
from db.crud import buy_crypto, sell_crypto, get_binance_price, get_base_price
from sqlalchemy.ext.asyncio import AsyncSession

PERCENTAGE_THRESHOLD_BUY = -0.5
PERCENTAGE_THRESHOLD_SELL = 0.5
TRADE_QUANTITY = 0.003


def price_change_percent(current_price: float, reference_price: float) -> float:
    return ((current_price - reference_price) / reference_price) * 100


async def simple_buy_strategy(db: AsyncSession, user_id: str,
                              symbol: str, trade_quantity: float = TRADE_QUANTITY):
    current_price = await get_binance_price(symbol)
    base_price = await get_base_price(db, symbol)
    change = price_change_percent(current_price, base_price)
    target_price = base_price * (1 + PERCENTAGE_THRESHOLD_BUY / 100)

    if change <= PERCENTAGE_THRESHOLD_BUY:
        trade_data = TradeCreate(
            user_id=user_id,
            symbol=symbol,
            quantity=trade_quantity,
            price=current_price
        )
        result = await buy_crypto(db, trade_data)
        return {
            "action": "buy",
            "symbol": symbol,
            "executed": True,
            "price": current_price,
            "change_percent": round(change, 2),
            "details": result
        }
    return {
        "action": "buy",
        "symbol": symbol,
        "executed": False,
        "price": current_price,
        "change_percent": round(change, 2),
        "message": f"Price change is {change:.2f}%, not below {PERCENTAGE_THRESHOLD_BUY}% "
                   f"Target price: {target_price:.2f} "
                   f"Base price: {base_price}"

    }


async def simple_sell_strategy(db: AsyncSession, user_id: str,
                               symbol: str, trade_quantity: float = TRADE_QUANTITY):
    current_price = await get_binance_price(symbol)
    base_price = await get_base_price(db, symbol)
    change = price_change_percent(current_price, base_price)
    target_price = base_price * (1 + PERCENTAGE_THRESHOLD_SELL / 100)

    if change >= PERCENTAGE_THRESHOLD_SELL:
        trade_data = TradeCreate(
            user_id=user_id,
            symbol=symbol,
            quantity=trade_quantity,
            price=current_price
        )
        result = await sell_crypto(trade_data, db)
        return {
            "action": "sell",
            "symbol": symbol,
            "executed": True,
            "price": current_price,
            "change_percent": round(change, 2),
            "details": result
        }
    return {
        "action": "sell",
        "symbol": symbol,
        "executed": False,
        "price": current_price,
        "change_percent": round(change, 2),
        "message": f"Price change is {change:.2f}%, not above {PERCENTAGE_THRESHOLD_SELL}% "
                   f"Target price: {target_price:.2f} "
                   f"Base price: {base_price}"
    }
