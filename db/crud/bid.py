from sqlalchemy import Integer, String, ForeignKey, Enum, select,update
from sqlalchemy.orm import Mapped, mapped_column, relationship
from db.session import SessionLocal

from db.models.bid import Bid
from datetime import datetime

async def create_bid(order_id: int, driver_id: int, price: float, eta_minutes: int = 0, comment: str = "") -> Bid:
    async with SessionLocal() as session:  # создаём сессию
        async with session.begin(): 
            bid = Bid(
                order_id=order_id,
                driver_id=driver_id,
                price=price,
                eta_minutes=eta_minutes,
                comment=comment,
                created_at=datetime.utcnow()
            )
            session.add(bid)
        await session.refresh(bid)  # обновляем объект после commit
        return bid
    


async def get_bid_by_id(bid_id: int) -> Bid | None:
    async with SessionLocal() as session:
        res = await session.execute(
            select(Bid).where(Bid.id == bid_id)
        )
        return res.scalar_one_or_none()
    
async def update_bid(bid_id: int, **kwargs) -> Bid | None:
    async with SessionLocal() as session:
        async with session.begin():
            res = await session.execute(select(Bid).where(Bid.id == bid_id))
            bid = res.scalar_one_or_none()
            if not bid:
                return None
            for key, value in kwargs.items():
                setattr(bid, key, value)
        await session.commit()
        await session.refresh(bid)
        return bid
    
# async def delete_bid(bid_id: int) -> bool:
#     async with SessionLocal() as session:
#         async with session.begin():
#             res = await session.execute(select(Bid).where(Bid.id == bid_id))
#             bid = res.scalar_one_or_none()
#             if not bid:
#                 return False
#             await session.delete(bid)
#         await session.commit()
#         return True