from contextlib import suppress

from aiogram.types import CallbackQuery, Message
from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.kbd import Button
from pymongo.errors import DuplicateKeyError

from tgbot.keyboards.reply import main_kb


async def on_female_selected(c: CallbackQuery, b: "Button", d: DialogManager):
    d.dialog_data["gender"] = False
    await d.next()


async def on_male_selected(c: CallbackQuery, b: "Button", d: DialogManager):
    d.dialog_data["gender"] = True
    await d.next()


async def on_age_success(_, __, manager: DialogManager, age: int):
    manager.dialog_data["age"] = age
    await manager.next()


async def on_age_error(message: Message, *args, **kwargs):
    await message.answer("Вы ввели некорректный возраст!")


async def on_nickname_success(m: Message, __, manager: DialogManager, nickname: str):
    await manager.middleware_data["repo"].users.add_nickname(m.from_user.id, nickname)
    await manager.middleware_data["repo"].users.add_age(m.from_user.id, manager.dialog_data["age"])
    await manager.middleware_data["repo"].users.add_gender(m.from_user.id, manager.dialog_data["gender"])
    gender = manager.dialog_data["gender"]
    await manager.done()
    await m.answer("Анкета успешно заполнена!")

    with suppress(DuplicateKeyError):
        await manager.middleware_data["mdb"].users.insert_one({
            "_id": m.from_user.id,
            "auto_search": False,
            "status": 0
        })

    await manager.middleware_data["mdb"].users.update_one({"_id": m.from_user.id},
                                                          {"$set": {"gender": gender}})

    searchers = await manager.middleware_data["mdb"].users.count_documents({"status": 1})
    await m.answer(
        "<b>☕ Начинай поиск собеседника!</b>\n"
        f"<i>👀 Участников в поиске:</i> <code>{searchers}</code>",
        reply_markup=main_kb
    )


async def on_nickname_error(message: Message, *args, **kwargs):
    await message.answer("Вы ввели некорректный никнейм!")
