

import asyncio

from aiogram import types
from aiogram.fsm.context import FSMContext

from telegram.keyboards import kb_get_number, ikb_admin_choice, ikb_admin_approve, choice_region, generate_ikb_order_control, generate_ikb_order_push

from db.models.user import Role, Status, User
from db.crud.user import create_user, get_user_by_tg_id, update_user, get_user_by_id
from db.crud.order import create_order, get_order_by_id, update_order, get_bid_by_driver_id
from db.crud.bid import create_bid, update_bid


from db.core import get_admins, take_order, bid_order, get_actual_orders_for_admin, get_max_bid_obj,get_all_bids_except_max
from db.models.order import Order, OrderStatus, OrderMode
from db.models.bid import Bid

from telegram.states import OrderForm, Get_Photos, AuctionBid
from telegram.texts import reg_finish,text_get_car_photos,generate_text_new_reg_user, generate_drive_info
from telegram.bot import bot
from telegram.handlers.admin import broadcast_order


from aiogram import Router

# Создаем Router
router_auction = Router()





async def notification_new_bid(message: types.Message, bid: Bid, amount):
    user = await get_user_by_id(bid.driver_id)
    await message.bot.send_message(user.tg_id, f"Ваша ставка на заказ {bid.order_id} перебита. Максимальная текущая ставка: {amount}")



@router_auction.message(AuctionBid.bid_amount)
async def process_bid_amount(message: types.Message, state: FSMContext):
    data = await state.get_data()
    order_id = data.get("order_id")
    print(message.text)

    if not order_id:

        return



    try:
        bid_amount = float(message.text)
        if bid_amount <= 0:
            raise ValueError("Ставка должна быть положительным числом.")
    except ValueError:
        await message.answer("Пожалуйста, введите корректную сумму ставки (положительное число).")
        return

    res = await bid_order(order_id, bid_amount)
    print(res)
    if res == OrderStatus.IN_PROGRESS:
        await message.answer(f"Заказ {order_id} уже взят другим водителем.")
    


    if res == OrderStatus.NEW:
        
        await message.answer(f"Ваша ставка для заказа {order_id} слишком низкая.")
    if res == True :
        print('Новая ставка')
        user = await get_user_by_tg_id(message.from_user.id)
        getbid = await get_max_bid_obj(order_id)
        check_bid = await get_bid_by_driver_id(order_id, user.id)
        

        if check_bid:

            print(getbid)
            
            if getbid.driver_id == user.id:
                await message.answer(f"Вашу ставку ещё никто не перебил")
            else:
                await update_bid(check_bid.id, price=bid_amount)
                await message.answer(f"Вы успешно сделали ставку {bid_amount} для заказа {order_id}. Ожидайте результатов аукциона.")
                bids_without_Max = await get_all_bids_except_max(order_id)
                tasks = []
                for i in bids_without_Max:
                    tasks.append(notification_new_bid(message,i,bid_amount))
                
                await asyncio.gather(*tasks, return_exceptions=True)

                
            return

        



        await create_bid(order_id=order_id, price=bid_amount, driver_id=user.id)
        bids_without_Max = await get_all_bids_except_max(order_id)
        tasks = []
        for i in bids_without_Max:
            tasks.append(notification_new_bid(message,i,bid_amount))
        
        await asyncio.gather(*tasks, return_exceptions=True)
        await message.answer(f"Вы успешно сделали ставку {bid_amount} для заказа {order_id}. Ожидайте результатов аукциона.")
        admins = await get_admins()
        tasks = []
        for admin in admins:
            text = generate_drive_info(user)
            tasks.append(message.bot.send_message(
                admin.tg_id,
                f"Новая ставка {bid_amount} для заказа {order_id} от водителя {message.from_user.id}\n {text}.",
            reply_markup=generate_ikb_order_push(order_id, message.from_user.id)))
        await asyncio.gather(*tasks, return_exceptions=True)
    await state.clear()


