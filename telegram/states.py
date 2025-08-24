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


class Get_Photos(StatesGroup):
    drive_ud = State()
    selfie = State()
    car_photos = State()
    sts = State()

class AuctionBid(StatesGroup):
    commments = State()
    bid_amount = State()