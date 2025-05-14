import requests
from datetime import datetime
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import insert
from db.db import get_db
from db.models import Price

router = APIRouter(prefix="/binance", tags=["Binance"])
BINANCE_API_URL = "https://api.binance.com/api/v3/klines"


@router.post("/import")
async def import_binance_data(symbol: str, interval: str, db: AsyncSession = Depends(get_db)):
    params = {
        "symbol": symbol,
        "interval": interval,
        "limit": 1000  # Максимальна кількість даних
    }

    response = requests.get(BINANCE_API_URL, params=params)
    data = response.json()

    # Перевірка на помилку в API
    if "code" in data:
        return {"error": f"Error from Binance API: {data['msg']}"}

    # Підготовка даних для запису в базу
    prices_to_insert = []
    for item in data:
        price_data = Price(
            symbol=symbol,
            timestamp=datetime.utcfromtimestamp(item[0] / 1000),  # Перетворення в datetime
            open=item[1],
            high=item[2],
            low=item[3],
            close=item[4],
            volume=item[5],
        )
        prices_to_insert.append(price_data)

    # Записуємо дані в базу
    async with db.begin():
        db.add_all(prices_to_insert)

    return {"message": f"Data for {symbol} imported successfully!"}
