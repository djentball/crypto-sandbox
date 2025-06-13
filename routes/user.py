from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from db.db import get_db
import db.crud as crud
import schemas
from db.models import User, Wallet, Price

router = APIRouter(prefix="/users", tags=["Users"])


@router.post("/", response_model=schemas.User)
async def create_user(user: schemas.UserCreate, db: AsyncSession = Depends(get_db)):
    existing = await crud.get_user_by_name(db, user.name)
    if existing:
        raise HTTPException(status_code=400, detail="User already exists")
    return await crud.create_user(db, user)


@router.get("/{user_id}", response_model=schemas.User)
async def get_user(user_id: str, db: AsyncSession = Depends(get_db)):
    user = await crud.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.get("/{user_id}/wallets", response_model=list[schemas.Wallet])
async def get_user_wallets(user_id: str, db: AsyncSession = Depends(get_db)):
    user = await crud.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return await crud.get_user_wallets(db, user_id)


@router.get("/{user_id}/balance")
async def user_balance(user_id: str, db: AsyncSession = Depends(get_db)):
    balance = await crud.get_user_balance(db, user_id)
    if balance is None:
        raise HTTPException(status_code=404, detail="User not found")
    return balance


@router.get("/", response_model=list[schemas.User])
async def get_all_users(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User))
    users = result.scalars().all()
    return users

