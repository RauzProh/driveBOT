from sqlalchemy import select, delete
from db.session import SessionLocal
from db.models.order_messages import OrderMessage


# создать запись
async def create_order_message(order_id: int, chat_id: int, message_id: int) -> OrderMessage:
    async with SessionLocal() as session:
        async with session.begin():
            order_msg = OrderMessage(
                order_id=order_id,
                chat_id=chat_id,
                message_id=message_id,
            )
            session.add(order_msg)
        await session.commit()
        await session.refresh(order_msg)
        return order_msg


# получить все сообщения по заказу
async def get_order_messages(order_id: int) -> list[OrderMessage]:
    async with SessionLocal() as session:
        result = await session.execute(
            select(OrderMessage).where(OrderMessage.order_id == order_id)
        )
        return result.scalars().all()


# получить одно сообщение по заказу и водителю
async def get_order_message(order_id: int, chat_id: int) -> OrderMessage | None:
    async with SessionLocal() as session:
        result = await session.execute(
            select(OrderMessage).where(
                OrderMessage.order_id == order_id,
                OrderMessage.chat_id == chat_id
            )
        )
        return result.scalar_one_or_none()


# удалить все сообщения заказа (например, когда заказ взят)
async def delete_order_messages(order_id: int) -> None:
    async with SessionLocal() as session:
        async with session.begin():
            await session.execute(
                delete(OrderMessage).where(OrderMessage.order_id == order_id)
            )
        await session.commit()


# удалить ОДНУ запись (по заказу и чату)
async def delete_order_message(order_id: int, chat_id: int) -> int:
    async with SessionLocal() as session:
        result = await session.execute(
            delete(OrderMessage).where(
                OrderMessage.order_id == order_id,
                OrderMessage.chat_id == chat_id
            )
        )
        await session.commit()
        return result.rowcount  # сколько строк удалили (0 или 1)