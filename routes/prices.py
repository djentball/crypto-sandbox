from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from db.db import get_db
from db import crud
from schemas import Price
from typing import List

router = APIRouter(prefix="/prices", tags=["Prices"])


@router.get("/", response_model=List[Price])
async def get_price_history(
    symbol: str = Query(..., description="Наприклад, BTCUSDT"),
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_db)
):
    return await crud.get_prices(db, symbol, limit)
