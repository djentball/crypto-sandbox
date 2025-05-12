from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from db.crud import set_base_price, get_base_price
from db.db import get_db
from db import crud
from schemas import TradeOut, TradeCreate, BasePriceUpdate
from typing import List
from fastapi.responses import JSONResponse

router = APIRouter(prefix="/trade", tags=["Trade"])


@router.post("/buy")
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

    trade_out = result["trade"]
    total_cost = result["total_cost"]

    trade_out_schema = TradeOut.from_orm(trade_out)  # Конвертація до Pydantic-схеми

    return {**trade_out_schema.dict(), "total_cost": total_cost}


@router.post("/sell", response_model=TradeOut)
async def sell_currency(trade: TradeCreate, db: AsyncSession = Depends(get_db)):
    trade.type = "sell"
    result = await crud.sell_crypto(trade, db)
    if isinstance(result, str) and "Insufficient" in result:
        raise HTTPException(status_code=400, detail=result)
    return result


@router.get("/history", response_model=List[TradeOut])
async def get_trade_history(symbol: str = None, limit: int = 100, db: AsyncSession = Depends(get_db)):
    return await crud.get_trades(db, symbol, limit)


@router.post("/base-price")
async def update_base_price(data: BasePriceUpdate, db: AsyncSession = Depends(get_db)):
    price = await set_base_price(db, data.symbol.upper(), data.price)
    return {"symbol": price.symbol, "price": price.price}


@router.get("/base-price/{symbol}")
async def fetch_base_price(symbol: str, db: AsyncSession = Depends(get_db)):
    price = await get_base_price(db, symbol.upper())
    return {"symbol": symbol.upper(), "price": price}