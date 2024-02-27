import random
from copy import copy

from aiogram_dialog import DialogManager, ChatEvent
from aiogram_dialog.api.entities import ShowMode, StartMode
from aiogram_dialog.widgets.kbd import ManagedRadio

from tgbot.dialogs.captcha.states import CaptchaStates
from tgbot.dialogs.profile.states import ProfileStates


async def on_emoji_selected(event: ChatEvent,
                            radio: ManagedRadio,
                            manager: DialogManager,
                            data: dict):
    if "chosen" not in manager.dialog_data:
        manager.dialog_data["chosen"] = {}

    manager.dialog_data["chosen"][radio.widget.widget_id] = radio.get_checked()

    if len(manager.dialog_data["chosen"]) == 4:
        if all([
            manager.dialog_data["chosen"].get("v1") == manager.start_data["captcha"][0],
            manager.dialog_data["chosen"].get("v2") == manager.start_data["captcha"][1],
            manager.dialog_data["chosen"].get("v3") == manager.start_data["captcha"][2],
            manager.dialog_data["chosen"].get("v4") == manager.start_data["captcha"][3]
        ]):
            await event.message.answer("Капча успешно пройдена!")
            await manager.middleware_data["repo"].users.captcha_done(event.from_user.id)
            manager.show_mode = ShowMode.EDIT
            await manager.done()
            await manager.start(ProfileStates.gender_state, show_mode=ShowMode.SEND)
        else:
            await event.message.answer("Капча пройдена неверно! Попробуйте заново")
            manager.show_mode = ShowMode.EDIT
            await manager.done()

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

            await manager.start(CaptchaStates.captcha_state, mode=StartMode.NEW_STACK,
                                data={"captcha": captcha, "variants": variants,
                                      "captcha_str": " ".join(captcha)})
