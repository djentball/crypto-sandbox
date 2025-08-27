from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from db.db import get_db
from schemas import FuturesPositionCreate, FuturesPositionOut
from db import crud

router = APIRouter(prefix="/futures", tags=["Futures"])


@router.post("/open", response_model=FuturesPositionOut)
async def open_position(
    position: FuturesPositionCreate,
    user_id: str = "64039ce2-822e-47c9-b87f-591fa10d3b93",
    db: AsyncSession = Depends(get_db)
):
    return await crud.open_futures_position(db, position, user_id)
