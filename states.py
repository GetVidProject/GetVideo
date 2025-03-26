from aiogram.fsm.state import StatesGroup, State


class AdminStates(StatesGroup):
    awaiting_password = State()
    authorized = State()
