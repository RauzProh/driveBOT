from aiogram import types
from aiogram.fsm.context import FSMContext
from aiogram.filters import CommandStart, Command
from aiogram import Router

from telegram.keyboards import kb_get_number

from db.crud.user import get_user_by_tg_id, create_user
from db.models.user import Role

router = Router()

# @router.message(CommandStart())
# async def start(message: types.Message, state: FSMContext):
#     await state.clear()

#     tg_id = message.from_user.id

#     # Проверяем, есть ли уже пользователь
#     user = await get_user_by_tg_id(tg_id)
#     if not user:
#         # Создаём нового пользователя с минимальными данными
#         user = await create_user(
#             tg_id=tg_id,
#             role=Role.DRIVER
#         )

#     await message.answer(
#         f"{message.from_user.first_name}, добро пожаловать в бот регистрации водителя!"
#     )
#     await message.answer(
#         "Для начала работы, пожалуйста, отправьте свой номер телефона.",
#         reply_markup=kb_get_number
#     )


# @router.message(Command("admin"))
# async def admin_command(message: types.Message):
#     tg_id = message.from_user.id
#     user = await get_user_by_tg_id(tg_id)
#     if user and user.role == Role.ADMIN:
#         await message.answer("Вы уже администратор.")
        
