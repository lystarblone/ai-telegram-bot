from aiogram.fsm.state import State, StatesGroup

class UploadStates(StatesGroup):
    waiting_auth_code = State()
    selecting_files = State()

class AskStates(StatesGroup):
    waiting_question = State()
    waiting_clarification = State()