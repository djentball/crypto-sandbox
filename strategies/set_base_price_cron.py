import asyncio
from db.db import get_db as get_session
from db.crud import set_base_price, get_binance_price


async def update_base_price_job():
    symbol = "BTCUSDT"
    async for session in get_session():
        new_price = await get_binance_price(symbol)
        await set_base_price(session, symbol, new_price)
        print(f"Base price for {symbol} updated to {new_price}")

if __name__ == "__main__":
    asyncio.run(update_base_price_job())
