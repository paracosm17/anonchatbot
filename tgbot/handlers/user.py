from contextlib import suppress

from aiogram import F
from aiogram import Router
from aiogram.filters import ChatMemberUpdatedFilter, MEMBER, KICKED
from aiogram.filters import Command, or_f
from aiogram.filters import CommandStart
from aiogram.types import ChatMemberUpdated
from aiogram.types import Message, CallbackQuery
from motor.core import AgnosticDatabase as MDB
from pymongo.errors import DuplicateKeyError

from aiogram_dialog import DialogManager
from aiogram_dialog.api.entities.modes import ShowMode
from tgbot.dialogs.profile.states import ProfileStates

from infrastructure.database.repo.requests import RequestsRepo
from tgbot.keyboards.inline import inline_builder
from tgbot.keyboards.reply import reply_builder, main_kb
from tgbot.misc.utils import ProfileSettings

user_router = Router()


@user_router.message(CommandStart())
async def user_start(message: Message, mdb: MDB):
    with suppress(DuplicateKeyError):
        await mdb.users.insert_one({
            "_id": message.from_user.id,
            "auto_search": False,
            "status": 0
        })

    searchers = await mdb.users.count_documents({"status": 1})
    await message.reply(
        "<b>☕ Начинай поиск собеседника!</b>\n"
        f"<i>👀 Участников в поиске:</i> <code>{searchers}</code>",
        reply_markup=main_kb
    )


@user_router.message(Command("profile"))
async def user_profile(message: Message, dialog_manager: DialogManager):
    await dialog_manager.start(ProfileStates.gender_state, show_mode=ShowMode.SEND)


@user_router.message(or_f(Command("search"), F.text.in_(["☕ Искать собеседника", "☕ Искать мужчин", "☕ Искать женщин"])))
async def search_interlocutor(message: Message, mdb: MDB, repo: RequestsRepo) -> None:
    user = await mdb.users.find_one({"_id": message.from_user.id})
    pattern = {
        "text": (
            "<b>☕ У тебя уже есть активный чат</b>\n"
            "<i>Используй команду /leave, чтобы покинуть чат</i>"
        ),
        "reply_markup": reply_builder("🚫 Прекратить диалог")
    }

    if user["status"] == 0:
        if message.text == "☕ Искать собеседника":
            await mdb.users.update_one({"_id": user["_id"]}, {"$set": {"status": 1, "find": 2}})
        if message.text == "☕ Искать мужчин":
            await mdb.users.update_one({"_id": user["_id"]}, {"$set": {"status": 1, "find": 1}})
        if message.text == "☕ Искать женщин":
            await mdb.users.update_one({"_id": user["_id"]}, {"$set": {"status": 1, "find": 0}})

        interlocutor = (await mdb.users.find_one({"status": 1, "find": user["gender"], "_id": {"$ne": user["_id"]}})
                        or
                        await mdb.users.find_one({"status": 1, "find": 2, "_id": {"$ne": user["_id"]}}))

        if not interlocutor:
            pattern["text"] = (
                "<b>👀 Ищу тебе собеседника...</b>\n"
                "<i>/cancel - Отменить поиск собеседника</i>"
            )
            pattern["reply_markup"] = reply_builder("❌ Отменить поиск")
        else:
            pattern["text"] = (
                "<b>🎁 Я нашел тебе собеседника, приятного общения!</b>\n"
                "<i>/next - Следующий собеседник</i>\n"
                "<i>/leave - Прекратить диалог</i>"
            )
            pattern["reply_markup"] = reply_builder("🚫 Прекратить диалог")

            await mdb.users.update_one(
                {"_id": user["_id"]}, {"$set": {"status": 2, "interlocutor": interlocutor["_id"]}}
            )
            await mdb.users.update_one(
                {"_id": interlocutor["_id"]}, {"$set": {"status": 2, "interlocutor": user["_id"]}}
            )
            await message.bot.send_message(interlocutor["_id"], **pattern)
    elif user["status"] == 1:
        pattern["text"] = (
            "<b>👀 УЖЕ ИЩУ тебе собеседника...</b>\n"
            "<i>/cancel - Отменить поиск собеседника</i>"
        )
        pattern["reply_markup"] = reply_builder("❌ Отменить поиск")

    await message.reply(**pattern)


@user_router.message(or_f(Command("cancel"), F.text == "❌ Отменить поиск"))
async def cancel_search(message: Message, mdb: MDB) -> None:
    user = await mdb.users.find_one({"_id": message.from_user.id})
    if user["status"] == 1:
        await mdb.users.update_one({"_id": user["_id"]}, {"$set": {"status": 0}})
        await message.reply(
            "<b>😔 Все.. больше никого искать не буду!</b>", reply_markup=main_kb
        )


@user_router.message(or_f(Command(commands=["leave", "stop"]), F.text == "🚫 Прекратить диалог"))
async def leave(message: Message, mdb: MDB) -> None:
    user = await mdb.users.find_one({"_id": message.from_user.id})
    if user["status"] == 2:
        await message.reply("<b>💬 Ты покинул чат!</b>", reply_markup=main_kb)
        await message.bot.send_message(
            user["interlocutor"], "<b>💬 Собеседник покинул чат!</b>", reply_markup=main_kb
        )

        await mdb.users.update_many(
            {"_id": {"$in": [user["_id"], user["interlocutor"]]}},
            {"$set": {"status": 0, "interlocutor": ""}}
        )

        # TODO: Реализовать автопоиск


@user_router.message(Command("next"))
async def next_interlocutor(message: Message, mdb: MDB) -> None:
    user = await mdb.users.find_one({"_id": message.from_user.id})
    if user["status"] == 2:
        await message.bot.send_message(
            user["interlocutor"], "<b>💬 Собеседник покинул чат!</b>", reply_markup=main_kb
        )
        await mdb.users.update_many(
            {"_id": {"$in": [user["_id"], user["interlocutor"]]}},
            {"$set": {"status": 0, "interlocutor": ""}}
        )


# @user_router.message(or_f(Command("profile"), F.text == "🍪 Профиль"))
async def profile(message: Message, mdb: MDB) -> None:
    user = await mdb.users.find_one({"_id": message.from_user.id})
    option = "🔴" if not user["auto_search"] else "🟢"

    await message.reply(
        f"Привет, <b>{message.from_user.first_name}</b>!",
        reply_markup=inline_builder(
            f"{option} Авто-поиск", ProfileSettings(value="auto_search_toggle").pack()
        )
    )


# @user_router.callback_query(ProfileSettings.filter(F.action == "change"))
async def change_profile_settings(query: CallbackQuery, callback_data: ProfileSettings, mdb: MDB) -> None:
    user = await mdb.users.find_one({"_id": query.from_user.id})

    if callback_data.value == "auto_search_toggle":
        if user["auto_search"]:
            await mdb.users.update_one({"_id": user["_id"]}, {"$set": {"auto_search": False}})
            option = "🔴"
        else:
            await mdb.users.update_one({"_id": user["_id"]}, {"$set": {"auto_search": True}})
            option = "🟢"

        await query.message.edit_reply_markup(
            reply_markup=inline_builder(
                f"{option} Авто-поиск", ProfileSettings(value="auto_search_toggle").pack()
            )
        )
    await query.answer()


@user_router.my_chat_member(ChatMemberUpdatedFilter(member_status_changed=KICKED))
async def user_blocked_bot(event: ChatMemberUpdated, repo: RequestsRepo):
    await repo.users.active_user(event.from_user.id, active=False)


@user_router.my_chat_member(ChatMemberUpdatedFilter(member_status_changed=MEMBER))
async def user_unblocked_bot(event: ChatMemberUpdated, repo: RequestsRepo):
    await repo.users.active_user(event.from_user.id, active=True)
