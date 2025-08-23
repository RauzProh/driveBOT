import asyncio
from db.session import engine
from db.base import Base
from db.models import User, Order, Bid  # <- импорт из db.models






async def init_models():
    async with engine.connect() as conn:
        await conn.run_sync(Base.metadata.create_all)
        print("All tables created.")
        await conn.commit()

if __name__ == "__main__":
    asyncio.run(init_models())