from aiogram.fsm.state import State, StatesGroup

class AnswerQuestion(StatesGroup):
    waiting_for_answer_text = State()

class MessageUser(StatesGroup):
    waiting_for_message_text = State()
