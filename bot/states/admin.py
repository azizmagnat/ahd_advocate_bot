from aiogram.fsm.state import State, StatesGroup

class AnswerQuestion(StatesGroup):
    waiting_for_answer_text = State()
