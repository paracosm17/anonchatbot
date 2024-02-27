import random
from copy import copy

from aiogram import Router
from aiogram_dialog import DialogManager

from aiogram.filters.command import CommandStart
from aiogram.types import Message

from tgbot.dialogs.captcha.states import CaptchaStates
from tgbot.keyboards.reply import main_kb

captcha_router = Router()


@captcha_router.message(CommandStart())
async def start(message: Message, dialog_manager: DialogManager):
    if not dialog_manager.middleware_data["profile"].captcha:
        await message.answer("ПРИВЕТСТВЕННОЕ СООБЩЕНИЕ")
        emodjis = ["⭐", "♥️", "🍄", "🔥", "⚽", "🏆", "🍎", "🌍", "🍪", "🧭", "🌼", "🎲"]
        captcha = random.sample(emodjis, k=4)
        variants = [[i] for i in captcha]
        for v in variants:
            tmp = copy(emodjis)
            tmp.remove(v[0])
            a = random.choice(tmp)
            tmp.remove(a)
            b = random.choice(tmp)
            v.extend((a, b))
            random.shuffle(v)
            del tmp

        await dialog_manager.start(CaptchaStates.captcha_state, data={"captcha": captcha, "variants": variants,
                                                                      "captcha_str": " ".join(captcha)})
    else:
        await message.answer("ПРИВЕТСТВЕННОЕ СООБЩЕНИЕ. ИЗМЕНИТЬ ПРОФИЛЬ - /profile")
        searchers = await dialog_manager.middleware_data["mdb"].users.count_documents({"status": 1})
        await message.answer(
            "<b>☕ Начинай поиск собеседника!</b>\n"
            f"<i>👀 Участников в поиске:</i> <code>{searchers}</code>",
            reply_markup=main_kb
        )
