import os
import asyncio
import sqlalchemy
from sqlalchemy.ext.asyncio import create_async_engine

DB_DRIVER = os.getenv("DB_DRIVER", "mysql+asyncmy")
DB_USER = os.getenv("DB_USER", "root")
DB_PASS = os.getenv("DB_PASS", "root")
DB_HOST = os.getenv("DB_HOST", "db")  # или 127.0.0.1
DB_PORT = os.getenv("DB_PORT", "3306")
DB_NAME = os.getenv("DB_NAME", "bot_db")

# подключение к серверу MySQL без базы
DATABASE_URL = f"mysql+asyncmy://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}?charset=utf8mb4"

async def ensure_database_exists():
    engine = create_async_engine(DATABASE_URL, echo=True)
    async with engine.begin() as conn:
        await conn.execute(
            sqlalchemy.text(f"CREATE DATABASE IF NOT EXISTS `{DB_NAME}` CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;")
        )
        print(f"Database '{DB_NAME}' is ready.")
    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(ensure_database_exists())
