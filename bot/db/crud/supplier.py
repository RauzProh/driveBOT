from sqlalchemy import Integer, String, ForeignKey, Enum, select,update
from sqlalchemy.orm import Mapped, mapped_column, relationship
from db.session import SessionLocal

from db.models.supplier import Supplier



async def create_suppliers(**kwargs) -> Supplier:
    async with SessionLocal() as session:
        async with session.begin():
            supplier = Supplier(**kwargs)
            session.add(supplier)
        await session.commit()
        await session.refresh(supplier)
        return supplier

async def get_all_supplier() -> list[Supplier]:
    async with SessionLocal() as session:
        res = await session.execute(select(Supplier))
        return res.scalars().all()  