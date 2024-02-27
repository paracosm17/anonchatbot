from aiogram.utils.keyboard import ReplyKeyboardBuilder, ReplyKeyboardMarkup
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove


def reply_builder(
    text: str | list[str],
    sizes: int | list[int] = 2,
    **kwargs
) -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()

    text = [text] if isinstance(text, str) else text
    sizes = [sizes] if isinstance(sizes, int) else sizes

    [
        builder.button(text=txt)
        for txt in text
    ]

    builder.adjust(*sizes)
    return builder.as_markup(resize_keyboard=True, **kwargs)


rmk = ReplyKeyboardRemove()

main_kb = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="☕ Искать собеседника"),
            KeyboardButton(text="☕ Искать мужчин"),
            KeyboardButton(text="☕ Искать женщин")
        ]
    ],
    resize_keyboard=True
)
