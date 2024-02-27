from aiogram_dialog import Window
from aiogram_dialog.widgets.input import TextInput
from aiogram_dialog.widgets.kbd import Button
from aiogram_dialog.widgets.text import Const

from tgbot.dialogs.profile.selected.filters import age_filter, nickname_filter
from tgbot.dialogs.profile.selected.profile import (on_age_error, on_age_success, on_male_selected, on_female_selected,
                                                    on_nickname_error, on_nickname_success)
from tgbot.dialogs.profile.states import ProfileStates


def gender_window():
    return Window(
        Const("Укажите свой пол"),
        Button(Const("Мужской"), id="male", on_click=on_male_selected),
        Button(Const("Женский"), id="female", on_click=on_female_selected),
        state=ProfileStates.gender_state
    )


def age_window():
    return Window(
        Const("Введите свой возраст"),
        TextInput(
            id="age",
            on_success=on_age_success,
            on_error=on_age_error,
            type_factory=int,
            filter=age_filter
        ),
        state=ProfileStates.age_state,
    )


def nickname_window():
    return Window(
        Const("Введите никнейм"),
        TextInput(
            id="nickname",
            on_success=on_nickname_success,
            on_error=on_nickname_error,
            type_factory=str,
            filter=nickname_filter
        ),
        state=ProfileStates.nickname_state,
    )
