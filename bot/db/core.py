from sqlalchemy import select, update, func

from db.session import SessionLocal
from db.models.user import User, Role, Status, Availability
from db.models.order import Order, OrderStatus, OrderMode
from db.models.bid import Bid
from db.crud.bid import create_bid



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

async def get_min_bid_obj(order_id: int) -> Bid | None:
    async with SessionLocal() as session:
        stmt = (
            select(Bid)
            .where(Bid.order_id == order_id)
            .order_by(Bid.price.asc(), Bid.created_at.asc())  # сортировка: сначала минимальная цена, потом по времени
        )
        result = await session.execute(stmt)
        bid = result.scalars().first()  # берём первую запись — минимальная цена
        return bid

async def get_min_bid(order_id):
    async with SessionLocal() as session:
        stmt = select(func.min(Bid.price)).where(Bid.order_id == order_id)
        res = await session.execute(stmt)
        return res.scalar()
    
async def get_all_bids_except_min(order_id: int) -> list[Bid]:
    async with SessionLocal() as session:
        # Сначала находим максимальную цену
        min_price_stmt = select(func.min(Bid.price)).where(Bid.order_id == order_id)
        min_price_res = await session.execute(min_price_stmt)
        min_price = min_price_res.scalar()

        if min_price is None:
            return []  # нет ставок

        # Выбираем все ставки кроме максимальной
        stmt = select(Bid).where(Bid.order_id == order_id, Bid.price > min_price)
        result = await session.execute(stmt)
        bids = result.scalars().all()
        return bids

async def bid_order(order_id: int, bid_amount: float) -> Order | OrderStatus | bool:
    async with SessionLocal() as session:
        stmt = select(Order).where(Order.id == order_id).with_for_update()
        res = await session.execute(stmt)
        order = res.scalar_one_or_none()

        print(order)
        if not order:
            return False  # заказ не найден
        print(order.status)
        print(order.mode)
        if order.mode == OrderMode.AUCTION and order.status == OrderStatus.NEW:
            min_bid = await get_min_bid(order.id)
            print(min_bid)
            if min_bid:
                if bid_amount >= min_bid:
                    return order.status
                
                else:
                    print('подходит ставка')
                    return True

            else:
                print('подходит ставка')
                return True  # возвращаем обновлённый объект
            
        if order.status != OrderStatus.NEW:
            return order.status
        return False  # заказ не в режиме аукциона или не новый
    

    
async def complete_order(order_id: int):
    async with SessionLocal() as session:
        stmt = select(Order).where(Order.id == order_id).with_for_update()
        res = await session.execute(stmt)
        order = res.scalar_one_or_none()

        if not order:
            return False  # заказ не найден

        if order.status == OrderStatus.IN_PROGRESS:
            order.status = OrderStatus.DONE
            if order.driver:
                order.driver.completed_orders += 1
            await session.commit()
            await session.refresh(order)
            return order  # возвращаем обновлённый объект

        return False  # заказ не в прогрессе, нельзя завершить
    
async def cancel_order(order_id: int):
    async with SessionLocal() as session:
        stmt = select(Order).where(Order.id == order_id).with_for_update()
        res = await session.execute(stmt)
        order = res.scalar_one_or_none()

        if not order:
            return False  # заказ не найден

        if order.status in [OrderStatus.NEW, OrderStatus.IN_PROGRESS]:
            order.status = OrderStatus.CANCELED
            await session.commit()
            await session.refresh(order)
            return order  # возвращаем обновлённый объект

        return False  # заказ нельзя отменить
    
async def set_driver_availability(tg_id: int, availability: Availability):
    async with SessionLocal() as session:
        stmt = select(User).where(User.tg_id == tg_id).with_for_update()
        res = await session.execute(stmt)
        user = res.scalar_one_or_none()

        if not user or user.role != Role.DRIVER:
            return False  # пользователь не найден или не водитель

        user.availability = availability
        await session.commit()
        await session.refresh(user)
        return user  # возвращаем обновлённый объект
    
async def get_actual_orders_for_admin() -> list[Order]:
    async with SessionLocal() as session:
        stmt = select(Order).where(Order.status.in_([OrderStatus.NEW, OrderStatus.IN_PROGRESS]))
        res = await session.execute(stmt)
        return res.scalars().all()
