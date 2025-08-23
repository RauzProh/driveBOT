from sqlalchemy import Integer, String, ForeignKey, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from db.session import SessionLocal

from db.models.order import Order, OrderStatus, OrderMode




async def create_order(**kwargs) -> Order:
    async with SessionLocal() as session:
        async with session.begin():
            order = Order(**kwargs)
            session.add(order)
        await session.commit()
        await session.refresh(order)
        return order
