# bot/api.py
from fastapi import FastAPI, Header, HTTPException, Path

from telegram.handlers.admin import broadcast_order, broadcast_order_to_admins
from telegram.bot import bot
from db.models.order import OrderStatus, Order

from db.crud.order import get_all_orders, create_order, update_order, get_order_by_id
from db.crud.order_messages import get_order_messages, delete_order_message
from db.crud.user import get_all_drivers, get_user_by_id

from schemas.order import OrderCreate

app = FastAPI()
API_KEY = "mysecret123"  # секрет для внутреннего API

@app.post("/create-order")
async def create_order_api(order: OrderCreate, x_api_key: str = Header(...)):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized")

    # маппинг из API-модели в модель БД
    db_order = await create_order(
        city=order.region,
        from_address=order.from_,
        to_address=order.to,
        scheduled_time=order.datetime,
        car_class=order.car_class,
        price=order.price,
        mode=order.mode,
        trip_number=order.flight,
        comments=order.comment,
        passenger_info=order.contact,
        status=OrderStatus.NEW
    )


    await broadcast_order(bot, db_order)
    await broadcast_order_to_admins(bot, db_order)


    return {"status": "ok", "order_id": db_order.id}


@app.post("/cancel-order/{order_id}")
async def cancel_order(
    order_id: int = Path(..., description="ID заказа для отмены"),
    x_api_key: str = Header(..., description="API ключ для авторизации")
):
    # Проверка ключа
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized")

    # Отменяем заказ
    try:
        revoke_order_id = int(order_id)
        order = await get_order_by_id(order_id=revoke_order_id)
        order_messages = await get_order_messages(order.id)
        for i in order_messages:
                try:
                    await bot.delete_message(i.chat_id, i.message_id)
                    await delete_order_message(revoke_order_id, i.chat_id)
                except Exception:
                    pass

        user = await get_user_by_id(order.driver_id)
        await update_order(order.id, status=OrderStatus.CANCELED)
        if user:
            await bot.send_message(user.tg_id, f"Заказ {order.id} анулирован")



        await update_order(order_id, status=OrderStatus.CANCELED)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при отмене: {str(e)}")

    return {"status": "ok", "order_id": order_id}



@app.get('/getorders')
async def get_orders(x_api_key: str = Header(...)):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized")
    orders = await get_all_orders()
    print(f"Fetched orders: {orders}")
    return {"orders": [order.__dict__ for order in orders]}


@app.get('/getdrivers')
async def get_orders(x_api_key: str = Header(...)):
    print(f"Received x_api_key: {x_api_key}")
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized")
    drivers = await get_all_drivers()
    print(f"Fetched drivers: {drivers}")
    return {"drivers": [driver.__dict__ for driver in drivers]}
    


