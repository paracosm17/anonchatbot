from aiogram.types import Message


def age_filter(x: Message):
    x = x.text
    if x.isdigit():
        x = int(x)
        return 16 <= x <= 60
    return False


def nickname_filter(x: Message):
    x = x.text
    if len(x) < 3 or len(x) > 32 or not x.isalnum():
        return False
    return True
