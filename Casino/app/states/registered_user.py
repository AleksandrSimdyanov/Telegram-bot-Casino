from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
import keyboards as kb
from app.database.requests import add_user

reg_user_router = Router()

class RegUser(StatesGroup):
    username = State()

@reg_user_router.message(Command("start"))
async def start_cmd(message: Message, state: FSMContext):
    await message.answer("Перед началом нужно зарегистрироваться.\n"
                         "Введите ваше Имя Фамилию")
    await state.set_state(RegUser.username)

@reg_user_router.message(RegUser.username)
async def add_username(message: Message, state: FSMContext):
    username = message.text
    tg_id = message.from_user.id
    if not username.strip():
        await message.answer("Имя не может быть пустым. Пожалуйста, введите ваше имя:")
        return
    try:
        await add_user(username=username, tg_id=tg_id)
        await message.answer("Добро пожаловать в наше Казино!\n"
                             "Выберите действие, нажав на кнопку, которую хотите.",
                             reply_markup=kb.start_kb)
    except Exception as e:
        await message.answer("Произошла ошибка при регистрации. Попробуйте позже.")
        print(f"Ошибка регистрации: {e}")
    finally:
        await state.clear()