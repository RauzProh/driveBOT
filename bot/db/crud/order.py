from sqlalchemy import Integer, String, ForeignKey, Enum, select,update
from sqlalchemy.orm import Mapped, mapped_column, relationship
from db.session import SessionLocal

from db.models.order import Order, OrderStatus, OrderMode
from db.models.bid import Bid




async def create_order(**kwargs) -> Order:
    async with SessionLocal() as session:
        async with session.begin():
            order = Order(**kwargs)
            session.add(order)
        await session.commit()
        await session.refresh(order)
        return order

async def get_order_by_id(order_id: int) -> Order | None:
    async with SessionLocal() as session:
        res = await session.execute(
            select(Order).where(Order.id == order_id)
        )
        return res.scalar_one_or_none()
    
async def get_all_orders() -> list[Order]:
    async with SessionLocal() as session:
        res = await session.execute(select(Order))
        return res.scalars().all()
    
async def update_order(order_id: int, **kwargs) -> Order | None:
    async with SessionLocal() as session:
        async with session.begin():
            res = await session.execute(select(Order).where(Order.id == order_id))
            order = res.scalar_one_or_none()
            if not order:
                return None
            for key, value in kwargs.items():
                setattr(order, key, value)
        await session.commit()
        await session.refresh(order)
        return order
    
async def get_bid_by_driver_id(order_id: int, driver_id: int) -> Bid | None:
    print("Проверка данных")
    print(order_id)
    print(driver_id)
    async with SessionLocal() as session:
        result = await session.execute(
            select(Bid).where(Bid.order_id == order_id, Bid.driver_id == driver_id)
        )
        bid = result.scalar_one_or_none()  # получаем один объект или None
        return bid