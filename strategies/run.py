import asyncio
from db.db import get_db as get_session
from strategies.simple_strategy import simple_buy_strategy, simple_sell_strategy

# USER_ID = "ddec577e-b919-442b-b76d-a2c97c7aabcd" #Stage User
SYMBOL = "BTCUSDT"
USER_ID = "dbfb7742-7cc2-4ddf-8dff-fed0e75ad352" #Prod User


async def run():
    async for db in get_session():
        trade_quantity = {
            'BTCUSDT': 0.003,
            'XRPUSDT': 50,
            'ETHUSDT': 0.005
        }

        for symbol, quantity in trade_quantity.items():
            buy_result = await simple_buy_strategy(db, USER_ID, symbol, quantity)
            sell_result = await simple_sell_strategy(db, USER_ID, symbol, quantity)
            print(f"Buy Result {symbol}:", buy_result)
            print(f"Sell Result {symbol}:", sell_result)

if __name__ == "__main__":
    asyncio.run(run())
