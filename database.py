from sqlmodel import SQLModel

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import URL

from decouple import config

# Create the database connection URL using our credentials from the .env file
SQLALCHEMY_DATABASE_URL = URL.create(
    "postgresql+asyncpg",
    username=config("USERNAME"),
    password=config("PASSWORD"),
    host=config("HOST"),
    port=config("PORT"),
    database=config("DATABASE"),
)

# Create the engine using the URL and enable future support and echoing of SQL statements
engine = create_async_engine(SQLALCHEMY_DATABASE_URL, echo=True)


# Define an async function to initialize our database
async def init_db(drop=True):
    async with engine.begin() as conn:
        if drop:
            await conn.run_sync(SQLModel.metadata.drop_all)
        await conn.run_sync(SQLModel.metadata.create_all)


# Create an async session maker to use in our FastAPI application
async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
