from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup


class OrderForm(StatesGroup):
    city = State()
    from_address = State()
    to_address = State()
    scheduled_time = State()
    car_class = State()
    price = State()
    mode = State()
    comments = State()
    passenger_info = State()
