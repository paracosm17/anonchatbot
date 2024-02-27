from aiogram_dialog import Dialog
from tgbot.dialogs.profile import windows


def profile_dialogs():
    return [
        Dialog(
            windows.gender_window(),
            windows.age_window(),
            windows.nickname_window()
        )
    ]
