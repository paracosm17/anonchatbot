import operator

from aiogram_dialog import Window
from aiogram_dialog.widgets.kbd import Radio
from aiogram_dialog.widgets.text import Const, Format

from tgbot.dialogs.captcha.getters import generate_captcha_buttons
from tgbot.dialogs.captcha.states import CaptchaStates
from tgbot.dialogs.captcha.selected.captcha import on_emoji_selected


def captcha_window():
    return Window(
        Format("Проверка на бота! Нажмите на эмодзи в таком порядке:\n{start_data[captcha_str]}"),
        Radio(
                Format("🔘 {item}"),
                Format("⚪️ {item}"),
                id="v1",
                item_id_getter=lambda item: item,
                items="a",
                on_state_changed=on_emoji_selected
        ),
        Radio(
            Format("🔘 {item}"),
            Format("⚪️ {item}"),
            id="v2",
            item_id_getter=lambda item: item,
            items="b",
            on_state_changed=on_emoji_selected
        ),
        Radio(
            Format("🔘 {item}"),
            Format("⚪️ {item}"),
            id="v3",
            item_id_getter=lambda item: item,
            items="c",
            on_state_changed=on_emoji_selected
        ),
        Radio(
            Format("🔘 {item}"),
            Format("⚪️ {item}"),
            id="v4",
            item_id_getter=lambda item: item,
            items="d",
            on_state_changed=on_emoji_selected
        ),
        state=CaptchaStates.captcha_state,
        getter=generate_captcha_buttons,
    )
