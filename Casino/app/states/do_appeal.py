from aiogram import F, Router
from aiogram.types import Message
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from app.database.requests import add_question
import keyboards

do_appeal_router = Router()

class Question(StatesGroup):
    asking_for_phone = State()
    question = State()
    phone_number = State()

@do_appeal_router.message(F.text == "Помощь")
async def show_question(message: Message, state: FSMContext):
    await message.answer("Доброго времени суток\n"
                         "Мы готовы выслушать ваш вопрос и ответить на него в кратчайшие сроки.")
    await state.set_state(Question.question)

@do_appeal_router.message(Question.question)
async def do_question(message: Message, state: FSMContext):
    question = message.text
    await state.update_data(question=question)
    await state.set_state(Question.asking_for_phone)
    await message.answer("Желаете ли вы оставить свои контакты?", reply_markup=keyboards.yes_no_kb)

@do_appeal_router.message(Question.asking_for_phone, F.text == "Да")
async def get_contact_yes(message: Message, state: FSMContext):
    await message.answer("Оставьте ваш номер телефона:", reply_markup=keyboards.phone_number_kb)
    await state.set_state(Question.phone_number)

@do_appeal_router.message(Question.asking_for_phone, F.text == "Нет")
async def get_contact_no(message: Message, state: FSMContext):
    user_id = message.from_user.id
    data = await state.get_data()
    await add_question(user_id=user_id,
                       question=data["question"],
                       status="new")
    await state.clear()
    await message.answer("Вопрос принят, ждите ответа!", reply_markup=keyboards.start_kb)

@do_appeal_router.message(Question.phone_number)
async def get_contact(message: Message, state: FSMContext):
    user_id = message.from_user.id
    phone = message.contact.phone_number
    data = await state.get_data()
    await add_question(user_id=user_id,
                       phone_number=phone,
                       question=data["question"],
                       status="new")
    await state.clear()
    await message.answer("Вопрос принят, ждите ответа!", reply_markup=keyboards.start_kb)