import asyncio
import datetime
from sqlalchemy import select
from db.db import async_session
from db.models import FuturesPosition
from db.crud import get_binance_price


async def check_take_profit():
    async with async_session() as db:
        positions = await db.execute(
            select(FuturesPosition).where(
                FuturesPosition.status == "open",
                FuturesPosition.take_profit_price.isnot(None)
            )
        )
        positions = positions.scalars().all()

        for pos in positions:
            current_price = await get_binance_price(pos.symbol)

            should_close = False
            if pos.side == "LONG" and current_price >= pos.take_profit_price:
                should_close = True
            elif pos.side == "SHORT" and current_price <= pos.take_profit_price:
                should_close = True

            if should_close:
                pos.status = "closed"
                pos.exit_price = current_price
                pos.exit_time = datetime.datetime.utcnow()
                pos.realized_pnl = (
                    (current_price - pos.entry_price) * pos.quantity * pos.leverage
                    if pos.side == "LONG"
                    else (pos.entry_price - current_price) * pos.quantity * pos.leverage
                )
                print(f"[{datetime.datetime.utcnow()}] TP hit for {pos.symbol} | Position closed")

        await db.commit()

if __name__ == "__main__":
    asyncio.run(check_take_profit())
