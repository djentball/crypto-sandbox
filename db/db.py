from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.ext.asyncio import async_sessionmaker

# DATABASE_URL = "sqlite+aiosqlite:///./db/trading.db"
DATABASE_URL = "sqlite+aiosqlite:///./db/trading.db?check_same_thread=False"

engine = create_async_engine(DATABASE_URL, echo=True)
async_session = async_sessionmaker(engine, expire_on_commit=False)

Base = declarative_base()


async def get_db():
    async with async_session() as session:
        yield session
