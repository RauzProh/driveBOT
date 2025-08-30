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
from collections import defaultdict

from aiogram import Router
import os
# Папка для сохранения фото
SAVE_PATH = "downloads"
os.makedirs(SAVE_PATH, exist_ok=True)

# Хранилище для медиа-групп
media_storage = {}
photo_list_xxx = []
dirks = []
albums = {}  # словарь для хранения фото по media_group_id
albums = defaultdict(list)
router_photos = Router()

@router_photos.message(Get_Photos.drive_ud)
async def order_city(message: types.Message, state: FSMContext):
    group_id = message.media_group_id
    albums[group_id].append(message)

    # Ожидаем, пока все фото придут (Телеграм шлёт их почти одновременно)
    await asyncio.sleep(1)  # небольшая задержка

    # Если это последний обработанный месседж альбома
    if albums[group_id][-1].message_id == message.message_id:
        photos = albums.pop(group_id)
        count = len(photos)
        spisok_photos = []
        for i, msg in enumerate(photos, start=1):
            # if not msg.photo:  # пропустить сообщения без фото
            #     continue
            # берём лучшее качество фото
            photo = msg.photo[-1]  
            file_id = photo.file_id  
            destination = f"downloads/{file_id}.jpg"
            # скачать через bot API
            await message.bot.download(file_id, destination=destination)
            spisok_photos.append(destination)

        await message.answer(f"✅ Получен альбом из {count} фото. Все скачаны.")
        await state.update_data(drive_ud=spisok_photos)
        await message.answer("📷  Загрузите свое фото на светлом фоне ")
        await state.set_state(Get_Photos.selfie)


@router_photos.message(Get_Photos.selfie)
async def order_city(message: types.Message, state: FSMContext):
    group_id = message.media_group_id
    albums[group_id].append(message)

    # Ожидаем, пока все фото придут (Телеграм шлёт их почти одновременно)
    await asyncio.sleep(1)  # небольшая задержка

    # Если это последний обработанный месседж альбома
    if albums[group_id][-1].message_id == message.message_id:
        photos = albums.pop(group_id)
        count = len(photos)
        spisok_photos = []
        for i, msg in enumerate(photos, start=1):
            # берём лучшее качество фото
            photo = msg.photo[-1]  
            file_id = photo.file_id  
            destination = f"downloads/{file_id}.jpg"
            # скачать через bot API
            await message.bot.download(file_id, destination=destination)
            spisok_photos.append(destination)

        await message.answer(f"✅ Получен альбом из {count} фото. Все скачаны.")
        await state.update_data(selfie=destination)
        await message.answer(text_get_car_photos)
        await state.set_state(Get_Photos.car_photos)


    # if message.photo:
    #         photo = message.photo[-1]
    #         file_info = await message.bot.get_file(photo.file_id)
    #         file_path = file_info.file_path
    #         destination = f"downloads/{photo.file_id}.jpg"
    #         await message.bot.download_file(file_path, destination)
    #         await state.update_data(selfie=destination)
    #         await message.answer(text_get_car_photos)
    #         await state.set_state(Get_Photos.car_photos)
    # else:
    #         await message.answer("📷  Загрузите свое фото на светлом фоне ")

@router_photos.message(Get_Photos.car_photos)
async def order_city(message: types.Message, state: FSMContext):
    group_id = message.media_group_id
    albums[group_id].append(message)

    # Ожидаем, пока все фото придут (Телеграм шлёт их почти одновременно)
    await asyncio.sleep(1)  # небольшая задержка

    # Если это последний обработанный месседж альбома
    if albums[group_id][-1].message_id == message.message_id:
        photos = albums.pop(group_id)
        count = len(photos)
        spisok_photos = []
        for i, msg in enumerate(photos, start=1):
            # берём лучшее качество фото
            photo = msg.photo[-1]  
            file_id = photo.file_id  
            destination = f"downloads/{file_id}.jpg"
            # скачать через bot API
            await message.bot.download(file_id, destination=destination)
            spisok_photos.append(destination)

        await message.answer(f"✅ Получен альбом из {count} фото. Все скачаны.")
        await state.update_data(car_photos=spisok_photos)
        await message.answer("📷 Сфотографируйте СТС с двух сторон и отправьте в чат.")
        await state.set_state(Get_Photos.sts)

    # if message.media_group_id and len(message.photo)>=2:
    #         photo = []
    #         for i in message.photo:
    #             photo = i
    #             file_info = await message.bot.get_file(photo.file_id)
    #             file_path = file_info.file_path
    #             destination = f"downloads/{photo.file_id}.jpg"
    #             await message.bot.download_file(file_path, destination)
    #             photo.append(destination)
    #         await state.update_data(car_photos=photo)
    #         await message.answer("📷 Сфотографируйте СТС с двух сторон и отправьте в чат.")
    #         await state.set_state(Get_Photos.sts)
    # else:
    #         await message.answer("📷  Пожалуйста, отправьте не менее 2 фотографий автомобиля - снаружи и изнутри.")

@router_photos.message(Get_Photos.sts)
async def order_city(message: types.Message, state: FSMContext):
    group_id = message.media_group_id
    albums[group_id].append(message)

    # Ожидаем, пока все фото придут (Телеграм шлёт их почти одновременно)
    await asyncio.sleep(1)  # небольшая задержка

    # Если это последний обработанный месседж альбома
    if albums[group_id][-1].message_id == message.message_id:
        photos = albums.pop(group_id)
        count = len(photos)
        spisok_photos = []
        for i, msg in enumerate(photos, start=1):
            # берём лучшее качество фото
            photo = msg.photo[-1]  
            file_id = photo.file_id  
            destination = f"downloads/{file_id}.jpg"
            # скачать через bot API
            await message.bot.download(file_id, destination=destination)
            spisok_photos.append(destination)

        await message.answer(f"✅ Получен альбом из {count} фото. Все скачаны.")
        await state.update_data(sts=spisok_photos)
        data = await state.get_data()
        #json with all photos
        documents = {
                "selfie": data['selfie'],
                "car_photos": data['car_photos'], #list of 2 photos
                "driver_license": data['drive_ud'], #list of 2 photos
                "sts": data['sts'] #list of 2 photos
            }
        user_get = await get_user_by_tg_id(message.from_user.id)
        get_text_reg_user = generate_text_new_reg_user(user_get)
        print(documents)
        reg_media = create_registration_media(documents, selfie_caption=get_text_reg_user)

        await update_user(message.from_user.id, documents=documents, status=Status.PENDING)
        await message.answer(reg_finish)
        print(123)
        print("\n\n\n")
        try:
            admins = await get_admins()
        except Exception as e:
            print(f"Ошибка при получении админов: {e}")
            admins = []
        print(admins)
        tasks = []

        for admin in admins:
            # 1. Отправляем альбом
            tasks.append(send_to_admin(message, reg_media, admin))

        # Выполняем параллельно все задачи
        await asyncio.gather(*tasks, return_exceptions=True)


    # if message.photo and len(message.photo)==2:
    #         photo = []
    #         for i in message.photo:
    #             photo = i
    #             file_info = await message.bot.get_file(photo.file_id)
    #             file_path = file_info.file_path
    #             destination = f"downloads/{photo.file_id}.jpg"
    #             await message.bot.download_file(file_path, destination)
    #             photo.append(destination)
    #         await state.update_data(sts=photo)
    #         data = await state.get_data()
    #         #json with all photos
    #         documents = {
    #             "selfie": data['selfie'],
    #             "car_photos": data['car_photos'], #list of 2 photos
    #             "driver_license": data['drive_ud'], #list of 2 photos
    #             "sts": data['sts'] #list of 2 photos
    #         }
    #         get_text_reg_user = generate_text_new_reg_user(user)

    #         reg_media = create_registration_media(documents, selfie_caption=get_text_reg_user)

    #         await update_user(message.from_user.id, documents=documents, status=Status.PENDING)
    #         await message.answer(reg_finish)
    #         admins = await get_admins()
    #         print(admins)
    #         user = await get_user_by_tg_id(message.from_user.id)
    #         tasks = []

    #         for admin in admins:
    #             # 1. Отправляем альбом
    #             tasks.append(send_to_admin(message, reg_media, admin))

    #         # Выполняем параллельно все задачи
    #         await asyncio.gather(*tasks, return_exceptions=True)
    # else:
    #         await message.answer("📷  Пожалуйста, отправьте фото СТС с обеих сторон.")


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

async def send_to_admin(message: types.Message, media, admin: User):
    await message.bot.send_media_group(admin.tg_id, media=media, parse_mode="Markdown")
    await message.bot.send_message(
                    admin.tg_id,
                    f"Выберите действие для - [{message.from_user.id}](tg://user?id={message.from_user.id})",
                    reply_markup=ikb_admin_approve(message.from_user.id, parse_mode="Markdown")  # если нужна клавиатура
                )
    return


