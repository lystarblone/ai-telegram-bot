from aiogram.fsm.state import State, StatesGroup

class UploadStates(StatesGroup):
    waiting_auth_code = State()

class AskStates(StatesGroup):
    waiting_question = State()

class ChatStates(StatesGroup):
    waiting_message = State()