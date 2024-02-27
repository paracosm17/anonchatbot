from aiogram_dialog import Dialog
from tgbot.dialogs.captcha import windows


def captcha_dialogs():
    return [
        Dialog(
            windows.captcha_window()
        )
    ]
