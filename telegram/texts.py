
from db.models.user import User

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



