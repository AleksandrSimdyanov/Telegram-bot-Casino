from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, FSInputFile
import keyboards as kb
import app.database.requests as rq

user_router = Router()

@user_router.message(F.text == "Игры")
async def check_games(message: Message):
    await message.answer("Вашему вниманию предоставляются все игры нашего скромного казино.\n"
                         "Выберите игру, в которую желаете сыграть", reply_markup = await kb.games_kb(back=True))

@user_router.callback_query(F.data == "back_menu")
async def back_menu(call: CallbackQuery):
    await call.message.answer("Добро пожаловать в наше Казино!\n"
                         "Выберите действие, нажав на кнопку, которую хотите.", reply_markup=kb.start_kb)
    await call.answer()

@user_router.message(F.text == "Баланс")
async def check_balance(message: Message):
    user_id = message.from_user.id
    user = await rq.get_user_by_tg_id(user_id)
    await message.answer(f"Ваш баланс: {user.balance}")

