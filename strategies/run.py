import asyncio
from db.db import get_db as get_session
from strategies.simple_strategy import simple_buy_strategy, simple_sell_strategy

# USER_ID = "ddec577e-b919-442b-b76d-a2c97c7aabcd" Stage User
SYMBOL = "BTCUSDT"
USER_ID = "dea9ff14-e356-4539-b7fb-423dd44b4804" #Prod User

async def run():
    async for db in get_session():
        buy_result = await simple_buy_strategy(db, USER_ID, SYMBOL)
        sell_result = await simple_sell_strategy(db, USER_ID, SYMBOL)
        print("Buy Result:", buy_result)
        print("Sell Result:", sell_result)

if __name__ == "__main__":
    asyncio.run(run())
