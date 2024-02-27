from aiogram.fsm.state import StatesGroup, State


class ProfileStates(StatesGroup):
    gender_state = State()
    age_state = State()
    nickname_state = State()
