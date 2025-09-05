from sqlalchemy import Integer, String, Enum, JSON, DECIMAL, TIMESTAMP, BigInteger
from sqlalchemy.orm import Mapped, mapped_column, relationship
from db.base import Base
import enum
from datetime import datetime

class Role(enum.Enum):
    UNREGISTERED = "unregistered"
    DRIVER = "driver"
    ADMIN = "admin"

class Status(enum.Enum):
    REGISTRATION = "registration"
    PENDING = "pending"
    APPROVED = "approved"
    DECLINED = "declined"

class Availability(enum.Enum):
    UNAVAILABLE = "unavailable"
    IN_WORK = "in_work"

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    tg_id: Mapped[int] = mapped_column(BigInteger, unique=True, nullable=False)
    role: Mapped[Role] = mapped_column(Enum(Role), default=Role.UNREGISTERED)

    full_name: Mapped[str] = mapped_column(String(255), nullable=True)
    phone: Mapped[str] = mapped_column(String(20), nullable=True)
    city: Mapped[str] = mapped_column(String(100), nullable=True)
    additional_cities: Mapped[str] = mapped_column(JSON, default=None)
    car_brand: Mapped[str] = mapped_column(String(100), nullable=True)
    car_model: Mapped[str] = mapped_column(String(100), nullable=True)
    car_color: Mapped[str] = mapped_column(String(50), nullable=True)
    car_number: Mapped[str] = mapped_column(String(20), nullable=True)
    car_photo: Mapped[str] = mapped_column(String(255), nullable=True)
    documents: Mapped[str] = mapped_column(JSON, nullable=True)
    
    status: Mapped[Status] = mapped_column(Enum(Status), default=Status.REGISTRATION)
    
    availability: Mapped[Availability] = mapped_column(Enum(Availability), default=Availability.UNAVAILABLE)
    
    rating: Mapped[float] = mapped_column(DECIMAL(3,2), nullable=True)

    completed_orders: Mapped[int] = mapped_column(Integer, default=0)
    cancelled_orders: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)

    orders: Mapped[list["Order"]] = relationship("Order", back_populates="driver")
