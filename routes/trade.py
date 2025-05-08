from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from db.db import get_db
from db import crud
from schemas import TradeOut, TradeCreate
from typing import List
from fastapi.responses import JSONResponse

router = APIRouter(prefix="/trade", tags=["Trade"])


@router.post("/buy", response_model=TradeOut)
async def buy_currency(trade: TradeCreate, db: AsyncSession = Depends(get_db)):
    trade.type = "buy"
    result = await crud.buy_crypto(db, trade)

    if isinstance(result, dict) and "error" in result:
        return JSONResponse(
            status_code=400,
            content={
                "detail": result["error"],
                "current_balance": result.get("current_balance"),
                "required": result.get("required")
            }
        )
    return result

@router.post("/sell", response_model=TradeOut)
async def sell_currency(trade: TradeCreate, db: AsyncSession = Depends(get_db)):
    trade.type = "sell"
    result = await crud.sell_crypto(db, trade)
    if isinstance(result, str) and "Insufficient" in result:
        raise HTTPException(status_code=400, detail=result)
    return result

@router.get("/history", response_model=List[TradeOut])
async def get_trade_history(symbol: str = None, limit: int = 100, db: AsyncSession = Depends(get_db)):
    return await crud.get_trades(db, symbol, limit)
