from sqlalchemy import select, update

from db.session import SessionLocal
from db.models.user import User, Role, Status, Availability

# Получить пользователя по Telegram ID
async def get_user_by_tg_id(tg_id: int) -> User | None:
    async with SessionLocal() as session:
        res = await session.execute(select(User).where(User.tg_id == tg_id))
        return res.scalar_one_or_none()

async def get_user_by_id(db_id: int) -> User | None:
    async with SessionLocal() as session:
        res = await session.execute(select(User).where(User.id == db_id))
        return res.scalar_one_or_none()

# Создать нового пользователя
async def create_user(
    tg_id: int,
    full_name: str | None = None,
    phone: str | None = None,
    city: str | None = None,
    additional_cities: list[str] | None = None,
    car_brand: str | None = None,
    car_model: str | None = None,
    car_color: str | None = None,
    car_number: str | None = None,
    car_photo: str | None = None,
    documents: dict | None = None,
    role: Role = Role.DRIVER,
    status: Status = Status.REGISTRATION,
    availability: Availability = Availability.UNAVAILABLE
) -> User:
    async with SessionLocal() as session:
        async with session.begin():
            user = User(
                tg_id=tg_id,
                full_name=full_name,
                phone=phone,
                city=city,
                additional_cities=additional_cities,
                car_brand=car_brand,
                car_model=car_model,
                car_color=car_color,
                car_number=car_number,
                car_photo=car_photo,
                documents=documents,
                role=role,
                status=status,
                availability=availability
            )
            session.add(user)
        await session.commit()
        await session.refresh(user)
        return user

# Обновить любые поля пользователя
async def update_user(tg_id: int, **kwargs) -> User | None:
    async with SessionLocal() as session:
        async with session.begin():
            res = await session.execute(select(User).where(User.tg_id == tg_id))
            user = res.scalar_one_or_none()
            if not user:
                return None
            for key, value in kwargs.items():
                if hasattr(user, key):
                    setattr(user, key, value)
        await session.commit()
        await session.refresh(user)
        return user

# Обновить только телефон
async def update_user_phone(tg_id: int, phone: str) -> User | None:
    return await update_user(tg_id, phone=phone)

# Проверка существования пользователя
async def user_exists(tg_id: int) -> bool:
    user = await get_user_by_tg_id(tg_id)
    return user is not None
