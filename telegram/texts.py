
from db.models.user import User
from db.models.order import Order

reg_finish = "Все шаги регистрации пройдены. Отлично! Мы рассматриваем заявки в течении 2-х рабочих дней. \
Вам придёт уведомление и вы сможете принимать заявки. Хорошего дня !"

print(reg_finish)

text_get_car_photos = "📷 Теперь - несколько фотографий автомобиля - снаружи и изнутри.\n\n\
Фотографируйте автомобиль в чистом состоянии, без лишних предметов внутри, в дневное время при хорошем освещении."


def generate_text_new_reg_user(user: User) -> str:
    text = f"Новый пользователь зарегистрировался в системе.\n\n\
ID: {user.id}\n\
Telegram ID: {user.tg_id}\n\
ФИО: {user.full_name}\n\
Телефон: {user.phone}\n\
Регион: {user.city}\n\
Марка/модель авто: {user.car_brand}\n\
Цвет/номер авто: {user.car_color} / {user.car_number}" 
    return text



def generate_text_drive_info(user: User) -> str:
    text = f"Водитель {user.full_name} {user.phone}, автомобиль {user.car_color} {user.car_brand} {user.car_number}"
    return text

def generate_drive_info(user: User) -> str:
    text = f"Водитель {user.full_name} {user.phone}, автомобиль {user.car_color} {user.car_brand} {user.car_number}"
    return text

def generate_auction_win_order(order: Order):
    text =f"Вы выиграли в аукционе на заказ {order.id}." 
    text+=f"🕐 Время: {order.scheduled_time}\n"
    text+=f"🚖 Класс авто: {order.car_class}\n"
    text+=f"⛳ {order.from_address} → {order.to_address}\n"
    text+=f"✈️ Номер рейса: {order.trip_number}\n"
    text+=f"💬 Комментарии: {order.comments or 'нет'}\n"
    text+=f"💰 Стоимость: {order.price}\n"
    text+=f"Связь с пассажиром: {order.passenger_info}"
    return text


reg_text = """Важно! Принимайте заказ только если гарантированно выполните.

Принятый заказ закрепляется только за вами, передача другим водителям запрещена!

Цена указанна фиксированная, обсудить детали или изменить условия нельзя.

Цена указана за весь запрос, включая доп услуги, если прописаны: встреча с табличкой, платная парковка, детское кресло и т.д.

Оплата по завершении заказа переводом на карточку любого банка! С пассажиров денег не берем, даже если дают (кроме чаевых, уточняйте).

Бесплатное ожидание в аэропорту 60 минут, на жд 20 минут, на адресе 10 минут, далее платно поминутно согласно вашему тарифу.

Отказ от принятых поездок производится самостоятельно, если осталось менее чем 1 час до заказа - Вам штраф 50% от суммы заказа.

Есть вопросы? - пишите логисту @elittransfer_com"""