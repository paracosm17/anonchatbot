from aiogram_dialog import DialogManager


async def generate_captcha_buttons(dialog_manager: DialogManager, **kwargs):
    variants = dialog_manager.start_data["variants"]
    return {"a": variants[0], "b": variants[1], "c": variants[2], "d": variants[3]}
