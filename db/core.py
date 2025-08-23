from sqlalchemy import select, update

from db.session import SessionLocal
from db.models.user import User, Role, Status, Availability
from db.models.order import Order, OrderStatus, OrderMode



async def get_admins():
    async with SessionLocal() as session:
        res = await session.execute(select(User).where(User.role == Role.ADMIN))
        return res.scalars().all()
    
async def get_drivers_for_order(city: str) -> list[User]:
    async with SessionLocal() as session:
        stmt = select(User).where(
            User.role == Role.DRIVER,
            User.status == Status.APPROVED,
            User.city == city
        )
        res = await session.execute(stmt)
        return res.scalars().all()



# async def take_order(order_id: int, driver_id: int):
#     async with SessionLocal() as session:
#         print("Attempting to take order")
#         print(f"Order ID: {order_id}, Driver ID: {driver_id}")
#         stmt = select(Order).where(Order.id == order_id).with_for_update()
#         res = await session.execute(stmt)
#         order = res.scalar_one_or_none()

#         if not order:
#             return False  # заказ не найден

#         if order.driver_id is None:
#             order.driver_id = driver_id
#             order.status = OrderStatus.IN_PROGRESS
#             await session.commit()
#             await session.refresh(order)
#             return order  # возвращаем обновлённый объект

#         return False  # заказ уже занят
async def take_order(order_id: int, tg_driver_id: int) -> Order | bool:
    async with SessionLocal() as session:
        # Найти заказ
        stmt_order = select(Order).where(Order.id == order_id).with_for_update()
        res_order = await session.execute(stmt_order)
        order = res_order.scalar_one_or_none()
        if not order:
            return False  # заказ не найден

        # Найти пользователя по Telegram ID
        stmt_user = select(User).where(User.tg_id == tg_driver_id)
        res_user = await session.execute(stmt_user)
        driver = res_user.scalar_one_or_none()
        if not driver:
            return False  # пользователь с таким Telegram ID не найден

        # Назначить заказ
        if order.driver_id is None:
            order.driver_id = driver.id  # именно внутренний id!
            order.status = OrderStatus.IN_PROGRESS
            await session.commit()
            await session.refresh(order)
            return order

        return False  # заказ уже занят