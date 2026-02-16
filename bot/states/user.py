from aiogram.fsm.state import State, StatesGroup

class AskQuestion(StatesGroup):
    waiting_for_question_text = State()

class SendProof(StatesGroup):
    waiting_for_screenshot = State()
