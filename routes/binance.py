from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from db.db import get_db
from db import crud
from schemas import PriceCreate
from datetime import datetime
import httpx

router = APIRouter(prefix="/binance", tags=["Binance"])

BINANCE_API_URL = "https://api.binance.com/api/v3/klines"


@router.post("/import")
async def import_binance_data(
    symbol: str = Query(..., description="Наприклад, BTCUSDT"),
    interval: str = Query("1m", description="Наприклад, 1m, 5m, 1h, 1d"),
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_db)
):
    params = {"symbol": symbol.upper(), "interval": interval, "limit": limit}

    async with httpx.AsyncClient() as client:
        response = await client.get(BINANCE_API_URL, params=params)
        response.raise_for_status()
        klines = response.json()

    added = 0
    for kline in klines:
        ts = datetime.fromtimestamp(kline[0] / 1000)

        if await crud.price_exists(db, symbol, ts):
            continue

        price = PriceCreate(
            symbol=symbol.upper(),
            timestamp=ts,
            open=float(kline[1]),
            high=float(kline[2]),
            low=float(kline[3]),
            close=float(kline[4]),
            volume=float(kline[5])
        )

        await crud.add_price(db, price)
        added += 1

    return {"message": f"Imported {added} new entries for {symbol}"}
