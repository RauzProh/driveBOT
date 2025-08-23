from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

from db.models.order import Order, OrderMode

kb_get_number = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📱 Отправить номер телефона", request_contact=True)]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )



ikb_admin_choice = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ accept", callback_data="desktop"),
            InlineKeyboardButton(text="❌ cancel", callback_data="mobile"),
        ],
        # [
        #     InlineKeyboardButton(text="комментарий", callback_data="comment"),
        # ]
    ]
)

def ikb_admin_approve(tg_id) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="✅ approve", callback_data=f"approve_{tg_id}"),
                InlineKeyboardButton(text="❌ decline", callback_data=f"decline_{tg_id}"),
            ],
            # [
            #     InlineKeyboardButton(text="комментарий", callback_data="comment"),
            # ]
        ]
    )

def build_order_buttons(order: Order) -> InlineKeyboardMarkup:
    buttons = []
    if order.mode == OrderMode.FCFS:
        buttons.append([InlineKeyboardButton(text="Взять заказ", callback_data=f"take_{order.id}")])
    else:
        buttons.append([InlineKeyboardButton(text="Сделать ставку", callback_data=f"bid_{order.id}")])

    return InlineKeyboardMarkup(inline_keyboard=buttons)