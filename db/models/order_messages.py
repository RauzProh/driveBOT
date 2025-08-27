from sqlalchemy import Integer, BigInteger, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from db.base import Base


class OrderMessage(Base):
    __tablename__ = "order_messages"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id"), nullable=False)
    chat_id: Mapped[int] = mapped_column(BigInteger, nullable=False)   # id чата (tg_id водителя)
    message_id: Mapped[int] = mapped_column(BigInteger, nullable=False)  # id сообщения в чате

    # уникальность (order_id + chat_id)
    __table_args__ = (
        UniqueConstraint("order_id", "chat_id", name="uix_order_chat"),
    )

    # связи
    order = relationship("Order", back_populates="messages")
