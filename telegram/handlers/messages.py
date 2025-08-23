import asyncio

from aiogram import types
from aiogram.fsm.context import FSMContext

from telegram.keyboards import kb_get_number, ikb_admin_choice, ikb_admin_approve,choice_region

from db.models.user import Role, Status, User
from db.crud.user import create_user, get_user_by_tg_id, update_user
from db.core import get_admins, take_order, get_actual_orders_for_admin
from db.models.order import Order, OrderStatus, OrderMode
from telegram.states import OrderForm, Get_Photos
from telegram.texts import reg_finish,text_get_car_photos,generate_text_new_reg_user

from aiogram import Router

# Создаем Router
router_message = Router()



import re

def is_valid_phone(phone: str) -> bool:
    """
    Проверяет валидность номера телефона.
    Допускаются форматы:
    +7XXXXXXXXXX
    8XXXXXXXXXX
    7XXXXXXXXXX
    """
    pattern = re.compile(r'^(?:\+7|7|8)\d{10}$')
    return bool(pattern.match(phone))

def is_valid_full_name(name: str) -> bool:
    """
    Проверяет ФИО.
    Допускаются только буквы, пробелы и дефисы.
    Должно быть 2 или 3 слова.
    """
    parts = name.strip().split()
    if len(parts) < 2 or len(parts) > 3:
        return False

    pattern = re.compile(r'^[А-ЯЁа-яёA-Za-z-]+$')
    for part in parts:
        if not pattern.match(part):
            return False
    return True

async def send_to_admin(message: types.Message, media, admin: User):
    await message.bot.send_media_group(admin.tg_id, media=media)
    await message.bot.send_message(
                    admin.tg_id,
                    f"Выберите действие для - {message.from_user.id}",
                    reply_markup=ikb_admin_approve(message.from_user.id)  # если нужна клавиатура
                )
    return

@router_message.message()
async def messages(message: types.Message, state: FSMContext):
    
    tg_id = message.from_user.id
    user = await get_user_by_tg_id(tg_id)
    if not user:
        # Создаём нового пользователя с минимальными данными
        user = await create_user(
            tg_id=tg_id,
            role=Role.DRIVER
        )
    
    
    res = await get_user_by_tg_id(message.from_user.id)

    print(res.__dict__)

    if message.text == 'Новый заказ' and res.role == Role.ADMIN:
        tg_id = message.from_user.id
        user = await get_user_by_tg_id(tg_id)
        if not user or user.role != Role.ADMIN:
            await message.answer("Доступ запрещён")
            return

        await state.set_state(OrderForm.city)
        await message.answer("Введите город заказа:")
        return
    
    if message.text == 'Управлять заказами' and res.role == Role.ADMIN:
        from_db_orders = await get_actual_orders_for_admin()

        if not from_db_orders:
            await message.answer("Нет актуальных заказов.")
            return

        msg = "Актуальные заказы:\n"
        for order in from_db_orders:
            msg += f"ID: {order.id}, Город: {order.city}, Статус: {order.status.value}\n"


        await message.answer(msg)
        return
    if res.phone is None:
        if message.contact:
            phone_number = message.contact.phone_number
            if is_valid_phone(phone_number):
                await message.answer(f"Ваш номер телефона {phone_number} успешно получен.")
                await update_user(message.from_user.id, phone=phone_number)
                # Здесь можно добавить переход к следующему шагу регистрации
                await message.answer("Пожалуйста, отправьте ваше ФИО.")

            else:
                await message.answer("Пожалуйста, отправьте корректный номер телефона.")
        elif message.text:
            if is_valid_phone(message.text):
                phone_number = message.text
                await message.answer(f"Ваш номер телефона {phone_number} успешно получен.")
                await update_user(message.from_user.id, phone=phone_number)
                # Здесь можно добавить переход к следующему шагу регистрации
                await message.answer("Пожалуйста, отправьте ваше ФИО.")

            else:
                await message.answer(
                    f"{message.from_user.first_name}, добро пожаловать в бот регистрации водителя ELITE TRANSFER!"
                )
                await message.answer("""
Этот бот позволит Вам начать работу в сервисе. Регистрация займёт 5 минут. 

Мы гарантируем конфиденциальность представленных данных и обязуемся не использовать их ни для каких целей, кроме рассмотрения вас для работы в сервисе.""")
                await message.answer(
                    "Для начала работы, пожалуйста, отправьте свой номер телефона.",
                    reply_markup=kb_get_number
    )           
        return


        
    if res.full_name is None:
        if is_valid_full_name(message.text):
            await message.answer(f"Ваше ФИО {message.text} успешно получено.")
            await update_user(message.from_user.id, full_name=message.text)
            await message.answer("Теперь, пожалуйста, отправьте регион, в котором вы обычно работаете.", reply_markup=choice_region)
        else:
            await message.answer("Пожалуйста, отправьте корректное ФИО (только буквы, пробелы и дефисы).")
        return
    if res.city is None:
        if message.text not in ["Краснодарский край", "Ставропольский край", "Крым"]:
            await message.answer("Пожалуйста, выберите регион из предложенных кнопок.")
            return
        await message.answer(f"Ваш город {message.text} успешно получен.")
        await update_user(message.from_user.id, city=message.text)
        await message.answer("Теперь, пожалуйста, отправьте марку и модель вашего авто.")
        return
    if res.car_brand is None:
        await message.answer(f"Марка/модель авто {message.text} успешно получена.")
        await update_user(message.from_user.id, car_brand=message.text)
        await message.answer("Теперь, пожалуйста, отправьте цвет авто.")
        return
    if res.car_color is None:
        await message.answer(f"Цвет авто {message.text} успешно получен.")
        await update_user(message.from_user.id, car_color=message.text)
        await message.answer("Теперь, пожалуйста, отправьте гос. номер авто.")
        return
    if res.car_number is None:
        await message.answer(f"Гос. номер авто {message.text} успешно получен.")
        await update_user(message.from_user.id, car_number=message.text)
        await message.answer("📷  Сфотографируйте ваше водительское удостоверение с обеих сторон и отправьте в чат. ")
        await state.set_state(Get_Photos.drive_ud)
        return
    if res.car_photo is None:
        if message.photo:
            photo = message.photo[-1]
            file_info = await message.bot.get_file(photo.file_id)
            file_path = file_info.file_path
            destination = f"downloads/{photo.file_id}.jpg"
            await message.bot.download_file(file_path, destination)
            await update_user(message.from_user.id, car_photo=destination)
            await message.answer("Фото авто успешно получено.")
            await message.answer("Теперь, пожалуйста, отправьте фото ваших документов.")
        else:
            await message.answer("Пожалуйста, отправьте фото вашего авто.")
        return
    if res.documents is None:
        if message.photo:
            photo = message.photo[-1]
            file_info = await message.bot.get_file(photo.file_id)
            file_path = file_info.file_path
            destination = f"downloads/{photo.file_id}.jpg"
            await message.bot.download_file(file_path, destination)
            await update_user(message.from_user.id, documents=destination, status=Status.PENDING)
            await message.answer("Фото документов успешно получено.")
            await message.answer(reg_finish)
            admins = await get_admins()
            print(admins)
            user = await get_user_by_tg_id(message.from_user.id)
            media = [ types.InputMediaPhoto(media=types.FSInputFile(user.car_photo), caption=f"Новый пользователь {message.from_user.id} ожидает подтверждения.") , types.InputMediaPhoto(media=types.FSInputFile(user.documents)) ]
            # Параллельная рассылка
            tasks = []

            for admin in admins:
                # 1. Отправляем альбом
                tasks.append(send_to_admin(message, media, admin))

            # Выполняем параллельно все задачи
            await asyncio.gather(*tasks, return_exceptions=True)
        else:
            await message.answer("Пожалуйста, отправьте фото ваших документов.")
        return
    print(res.status)
    if res.status == Status.PENDING or res.status == Status.REGISTRATION:
        # await update_user(message.from_user.id, status="PENDING")
        await message.answer("Ваша регистрация уже завершена и находится на рассмотрении.")
        await message.answer("Ожидайте одобрения от администрации.")
        print(123)
        print("\n\n\n")
        admins = await get_admins()
        print(admins)
        user = await get_user_by_tg_id(message.from_user.id)
        media = [ types.InputMediaPhoto(media=types.FSInputFile(user.car_photo), caption=f"Новый пользователь {message.from_user.id} ожидает подтверждения.") , types.InputMediaPhoto(media=types.FSInputFile(user.documents)) ]
        # Параллельная рассылка
        tasks = []

        for admin in admins:
            # 1. Отправляем альбом
            tasks.append(message.bot.send_media_group(admin.tg_id, media=media))
            
            # 2. Отправляем отдельное сообщение с текстом/клавиатурой
            tasks.append(
                message.bot.send_message(
                    admin.tg_id,
                    f"Выберите действие для - {message.from_user.id}",
                    reply_markup=ikb_admin_approve(message.from_user.id)  # если нужна клавиатура
                )
            )

        # Выполняем параллельно все задачи
        await asyncio.gather(*tasks, return_exceptions=True)





@router_message.callback_query(lambda c: c.data.startswith("take_"))
async def take_order_callback(callback_query: types.CallbackQuery):
    order_id = int(callback_query.data.split("_")[1])
    print("Order ID:", order_id)
    print(callback_query.from_user.id)
    res = await take_order(order_id, callback_query.from_user.id)
    if not res:
        await callback_query.answer(f"Извините, заказ {order_id} уже взят другим водителем.", show_alert=True)
    else:
        await callback_query.answer(f"Вы успешно взяли заказ {order_id}.", show_alert=True)
        await callback_query.bot.send_message(
            callback_query.from_user.id,
            f"Пассажир: {res.passenger_info}. Телефон: {res.passenger_phone}"
        )
        await callback_query.message.edit_reply_markup()  # Убираем кнопки после успешного



@router_message.message(Get_Photos.drive_ud)
async def order_city(message: types.Message, state: FSMContext):
    if message.photo and len(message.photo)==2:
            photo = []
            for i in message.photo:
                photo = i
                file_info = await message.bot.get_file(photo.file_id)
                file_path = file_info.file_path
                destination = f"downloads/{photo.file_id}.jpg"
                await message.bot.download_file(file_path, destination)
                photo.append(destination)
            await state.update_data(drive_ud=photo)
            await message.answer("📷  Загрузите свое фото на светлом фоне ")
            await state.set_state(Get_Photos.selfie)
    else:
            await message.answer("📷  Сфотографируйте ваше водительское удостоверение с обеих сторон и отправьте в чат.")

@router_message.message(Get_Photos.selfie)
async def order_city(message: types.Message, state: FSMContext):
    if message.photo:
            photo = message.photo[-1]
            file_info = await message.bot.get_file(photo.file_id)
            file_path = file_info.file_path
            destination = f"downloads/{photo.file_id}.jpg"
            await message.bot.download_file(file_path, destination)
            await state.update_data(selfie=destination)
            await message.answer(text_get_car_photos)
            await state.set_state(Get_Photos.car_photos)
    else:
            await message.answer("📷  Загрузите свое фото на светлом фоне ")

@router_message.message(Get_Photos.car_photos)
async def order_city(message: types.Message, state: FSMContext):
    if message.photo and len(message.photo)>=2:
            photo = []
            for i in message.photo:
                photo = i
                file_info = await message.bot.get_file(photo.file_id)
                file_path = file_info.file_path
                destination = f"downloads/{photo.file_id}.jpg"
                await message.bot.download_file(file_path, destination)
                photo.append(destination)
            await state.update_data(car_photos=photo)
            await message.answer("📷 Сфотографируйте СТС с двух сторон и отправьте в чат.")
            await state.set_state(Get_Photos.sts)
    else:
            await message.answer("📷  Пожалуйста, отправьте не менее 2 фотографий автомобиля - снаружи и изнутри.")

@router_message.message(Get_Photos.sts)
async def order_city(message: types.Message, state: FSMContext):
    if message.photo and len(message.photo)==2:
            photo = []
            for i in message.photo:
                photo = i
                file_info = await message.bot.get_file(photo.file_id)
                file_path = file_info.file_path
                destination = f"downloads/{photo.file_id}.jpg"
                await message.bot.download_file(file_path, destination)
                photo.append(destination)
            await state.update_data(sts=photo)
            data = await state.get_data()
            #json with all photos
            documents = {
                "selfie": data['selfie'],
                "car_photos": data['car_photos'], #list of 2 photos
                "driver_license": data['drive_ud'], #list of 2 photos
                "sts": data['sts'] #list of 2 photos
            }
            get_text_reg_user = generate_text_new_reg_user(user)

            reg_media = create_registration_media(documents, selfie_caption=get_text_reg_user)

            await update_user(message.from_user.id, documents=documents, status=Status.PENDING)
            await message.answer(reg_finish)
            admins = await get_admins()
            print(admins)
            user = await get_user_by_tg_id(message.from_user.id)
            # media = [ types.InputMediaPhoto(media=types.FSInputFile(user.car_photo), caption=get_text_reg_user) , types.InputMediaPhoto(media=types.FSInputFile(user.documents)) ]
            # # Параллельная рассылка
            tasks = []

            for admin in admins:
                # 1. Отправляем альбом
                tasks.append(send_to_admin(message, reg_media, admin))

            # Выполняем параллельно все задачи
            await asyncio.gather(*tasks, return_exceptions=True)
    else:
            await message.answer("📷  Пожалуйста, отправьте фото СТС с обеих сторон.")


from typing import Dict, List

def create_registration_media(documents: Dict[str, List[str]], selfie_caption: str = None) -> List[types.InputMediaPhoto]:
    """
    Создаёт список InputMediaPhoto для регистрации пользователя.

    :param documents: JSON с файлами пользователя
                      {
                          "selfie": str,
                          "car_photos": List[str],
                          "driver_license": List[str],
                          "sts": List[str]
                      }
    :param selfie_caption: подпись к селфи (только к первой фотографии)
    :return: список InputMediaPhoto для отправки через send_media_group
    """
    media: List[types.InputMediaPhoto] = []

    # 1. Сначала все фото автомобиля
    for car_photo in documents.get("car_photos", []):
        media.append(types.InputMediaPhoto(media=types.FSInputFile(car_photo)))

    # 2. Селфи с подписью
    if selfie := documents.get("selfie"):
        media.insert(0, types.InputMediaPhoto(media=types.FSInputFile(selfie), caption=selfie_caption))

    # 3. Документы: водительское удостоверение и СТС
    for doc_type in ["driver_license", "sts"]:
        for doc_photo in documents.get(doc_type, []):
            media.append(types.InputMediaPhoto(media=types.FSInputFile(doc_photo)))

    return media


