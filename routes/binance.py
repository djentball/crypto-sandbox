import requests
from datetime import datetime
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import insert
from db.db import get_db
from db.models import Price

router = APIRouter(prefix="/binance", tags=["Binance"])
BINANCE_API_URL = "https://api.binance.com/api/v3/klines"


def get_klines_binance(symbol: str, interval: str):
    params = {
        "symbol": symbol,
        "interval": interval,
        "limit": 1000
    }

    response = requests.get(BINANCE_API_URL, params=params)
    data = response.json()
    if "code" in data:
        return {"error": f"Error from Binance API: {data['msg']}"}
    return data


@router.get("/get_rsi")
async def get_rsi(symbol: str, interval: str):
    data = get_klines_binance(symbol, interval)
    values = [float(candle[4]) for candle in data]
    timestamps = [int(candle[0]) for candle in data]
    window = 14
    gains = []
    losses = []

    for i in range(1, window + 1):
        change = values[i] - values[i - 1]
        gains.append(max(0, change))
        losses.append(max(0, -change))

    avg_gain = sum(gains) / window
    avg_loss = sum(losses) / window

    rsi = []
    if avg_loss == 0:
        rsi.append(100)
    else:
        rs = avg_gain / avg_loss
        rsi.append(100 - (100 / (1 + rs)))

    for i in range(window + 1, len(values)):
        change = values[i] - values[i - 1]
        gain = max(0, change)
        loss = max(0, -change)

        avg_gain = (avg_gain * (window - 1) + gain) / window
        avg_loss = (avg_loss * (window - 1) + loss) / window

        if avg_loss == 0:
            rsi.append(100)
        else:
            rs = avg_gain / avg_loss
            rsi.append(100 - (100 / (1 + rs)))

    return [None] * window + rsi


@router.post("/import")
async def import_binance_data(symbol: str, interval: str, db: AsyncSession = Depends(get_db)):
    data = get_klines_binance(symbol, interval)

    prices_to_insert = []
    for item in data:
        price_data = Price(
            symbol=symbol,
            timestamp=datetime.utcfromtimestamp(item[0] / 1000),
            open=item[1],
            high=item[2],
            low=item[3],
            close=item[4],
            volume=item[5],
        )
        prices_to_insert.append(price_data)

    async with db.begin():
        db.add_all(prices_to_insert)

    return {"message": f"Data for {symbol} imported successfully!"}


BINANCE_FUTURES_API = "https://fapi.binance.com"


def get_futures_price(symbol: str) -> float:
    url = f"{BINANCE_FUTURES_API}/fapi/v1/ticker/price?symbol={symbol}"

    try:
        response = requests.get(url)
        response.raise_for_status()

        data = response.json()
        price = float(data["price"])

        return price

    except requests.exceptions.HTTPError as http_err:
        print(f"Помилка HTTP: {http_err}")
        raise
    except Exception as err:
        print(f"Виникла інша помилка: {err}")
        raise


if __name__ == "__main__":
    try:
        btc_price = get_futures_price("BTCUSDT")
        print(f"Поточна ціна ф'ючерсу BTCUSDT: {btc_price}")

        eth_price = get_futures_price("ETHUSDT")
        print(f"Поточна ціна ф'ючерсу ETHUSDT: {eth_price}")

        get_futures_price("NONEXISTENTCOIN")

    except requests.exceptions.HTTPError as e:
        print(f"\nНе вдалося отримати ціну: {e.response.status_code} {e.response.reason}")
    except KeyError:
        print("\nНе вдалося обробити відповідь від API: не знайдено ключ 'price'.")