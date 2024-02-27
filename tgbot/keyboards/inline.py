from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardMarkup
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove


def inline_builder(
    text: str | list[str],
    callback_data: str | list[str],
    sizes: int | list[int] = 2,
    **kwargs
) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    text = [text] if isinstance(text, str) else text
    callback_data = [callback_data] if isinstance(callback_data, str) else callback_data
    sizes = [sizes] if isinstance(sizes, int) else sizes

    [
        builder.button(text=txt, callback_data=cb)
        for txt, cb in zip(text, callback_data)
    ]

    builder.adjust(*sizes)
    return builder.as_markup(**kwargs)
