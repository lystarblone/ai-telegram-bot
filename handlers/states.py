from aiogram.fsm.state import State, StatesGroup

class UploadStates(StatesGroup):
    waiting_auth_code = State()