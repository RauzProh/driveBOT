from datetime import datetime

from aiogram import types
from aiogram.fsm.context import FSMContext
from aiogram.filters import CommandStart, Command
from aiogram import Router

from telegram.states import OrderForm
from telegram.keyboards import kb_get_number, build_order_buttons, admin_panel, choice_region, choice_order_mod
from telegram.bot import bot

from db.crud.user import get_user_by_tg_id, create_user, update_user
from db.crud.order import create_order
from db.models.user import Role, Status
from db.models.order import Order, OrderStatus, OrderMode
from db.core import get_drivers_for_order

router_admin = Router()


async def broadcast_order(bot, order: Order):
    drivers = await get_drivers_for_order(order.city)
    for driver in drivers:
        await bot.send_message(
            driver.tg_id,
            f"❗ Новый заказ №{order.id}:\n"
            f"🕐 Время: {order.scheduled_time}\n"
            f"🚖 Класс авто: {order.car_class}\n"
            f"⛳ {order.from_address} → {order.to_address}\n"
            f"💬 Комментарии: {order.comments or 'нет'}\n"
            f"💰 Стоимость: {order.price if order.price else 'Аукцион'}",
            reply_markup=build_order_buttons(order)
        )





@router_admin.message(Command("admin"))
async def admin_command(message: types.Message):
    tg_id = message.from_user.id
    user = await get_user_by_tg_id(tg_id)
    if user and user.role == Role.ADMIN:
        await message.answer("Админ-панель", reply_markup=admin_panel)


@router_admin.callback_query(lambda c: c.data.startswith("approve_"))
async def accept_user_callback(callback_query: types.CallbackQuery):
    tg_id = int(callback_query.data.split("_")[1])
    user = await get_user_by_tg_id(tg_id)
    if user:
        await update_user(tg_id, status=Status.APPROVED)
        await callback_query.bot.send_message(tg_id, "Ваша регистрация одобрена! Теперь вы можете использовать бота.")
        await callback_query.message.edit_reply_markup()



@router_admin.callback_query(lambda c: c.data.startswith("decline_"))
async def reject_user_callback(callback_query: types.CallbackQuery):
    tg_id = int(callback_query.data.split("_")[1])
    user = await get_user_by_tg_id(tg_id)
    if user and user.role != Role.ADMIN:
        await update_user(tg_id, status=Status.DECLINED)
        await callback_query.bot.send_message(tg_id, "Регистрация отклонена. Пожалуйста, свяжитесь с поддержкой.")
        await callback_query.message.edit_reply_markup()


# ----------------- FSM Handlers -----------------
@router_admin.message(Command("new_order"))
async def new_order_start(message: types.Message, state: FSMContext):
    tg_id = message.from_user.id
    user = await get_user_by_tg_id(tg_id)
    if not user or user.role != Role.ADMIN:
        await message.answer("Доступ запрещён")
        return

    await state.set_state(OrderForm.city)
    await message.answer("Введите регион заказа:", reply_markup=choice_region)


@router_admin.message(OrderForm.city)
async def order_city(message: types.Message, state: FSMContext):
    if message.text not in ["Краснодарский край", "Ставропольский край", "Крым"]:
        await message.answer("Пожалуйста, выберите регион из предложенных вариантов.")
        return
    await state.update_data(city=message.text)
    await state.set_state(OrderForm.from_address)
    await message.answer("Откуда (адрес подачи):")


@router_admin.message(OrderForm.from_address)
async def order_from_address(message: types.Message, state: FSMContext):
    await state.update_data(from_address=message.text)
    await state.set_state(OrderForm.to_address)
    await message.answer("Куда (адрес назначения):")


@router_admin.message(OrderForm.to_address)
async def order_to_address(message: types.Message, state: FSMContext):
    await state.update_data(to_address=message.text)
    await state.set_state(OrderForm.scheduled_time)
    await message.answer("Дата и время подачи (формат: YYYY-MM-DD HH:MM):")


@router_admin.message(OrderForm.scheduled_time)
async def order_time(message: types.Message, state: FSMContext):
    try:
        dt = datetime.strptime(message.text, "%Y-%m-%d %H:%M")
        await state.update_data(scheduled_time=dt)
        await state.set_state(OrderForm.car_class)
        await message.answer("Класс авто (эко/комфорт/бизнес):")
    except ValueError:
        await message.answer("Неверный формат. Попробуйте снова.")


@router_admin.message(OrderForm.car_class)
async def order_car_class(message: types.Message, state: FSMContext):
    await state.update_data(car_class=message.text)
    await state.set_state(OrderForm.price)
    await message.answer("Введите стоимость заказа (или оставьте пустым для аукциона):")


@router_admin.message(OrderForm.price)
async def order_price(message: types.Message, state: FSMContext):
    text = message.text.strip()
    price = float(text) if text else None
    await state.update_data(price=price)
    await state.set_state(OrderForm.mode)
    await message.answer("Режим заказа: FCFS или AUCTION?", reply_markup=choice_order_mod)


@router_admin.message(OrderForm.mode)
async def order_mode(message: types.Message, state: FSMContext):
    mode_text = message.text.lower()
    if mode_text not in ["fcfs", "auction"]:
        await message.answer("Неверный режим. Введите FCFS или AUCTION.")
        return
    await state.update_data(mode=OrderMode.FCFS if mode_text == "fcfs" else OrderMode.AUCTION)
    await state.set_state(OrderForm.comments)
    await message.answer("Комментарии к заказу (опционально):")


@router_admin.message(OrderForm.comments)
async def order_comments(message: types.Message, state: FSMContext):
    await state.update_data(comments=message.text)
    await state.set_state(OrderForm.passenger_info)
    await message.answer("Контактная информация пассажира:")


@router_admin.message(OrderForm.passenger_info)
async def finish_order(message: types.Message, state: FSMContext):
    await state.update_data(passenger_info=message.text)
    data = await state.get_data()

    order = await create_order(
        city=data['city'],
        from_address=data['from_address'],
        to_address=data['to_address'],
        scheduled_time=data['scheduled_time'],
        car_class=data['car_class'],
        price=data.get('price'),
        mode=data['mode'],
        comments=data.get('comments'),
        passenger_info=data.get('passenger_info'),
        status=OrderStatus.NEW
    )

    await broadcast_order(bot, order)
    await message.answer("Заказ опубликован и разослан водителям!")
    await state.clear()