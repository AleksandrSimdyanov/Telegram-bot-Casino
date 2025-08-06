from aiogram import F, Router
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
import app.database.requests as rq
import keyboards as kb
import random
from typing import Optional, Tuple
from app.database.models import User, Game
from Games.Dice import DiceGame

play_dice_router = Router()

class DiceState(StatesGroup):
    waiting_bet = State()
    waiting_number = State()

    @staticmethod
    async def validate_bet(tg_id: int, bet: int) -> Tuple[bool, str, Optional[User], Optional[Game]]:
        user = await rq.get_user_by_tg_id(tg_id)
        game = await rq.get_game_by_id(3)  # ID игры "Кости"

        if not user or not game:
            return False, "Ошибка загрузки данных", None, None
        if bet < game.min_bet:
            return False, f"Минимальная ставка: {game.min_bet}", user, game
        if bet > game.max_bet:
            return False, f"Максимальная ставка: {game.max_bet}", user, game
        if bet > user.balance:
            return False, "Недостаточно средств", user, game
        return True, "", user, game


@play_dice_router.callback_query(F.data == "game_3")
async def start_dice(call: CallbackQuery, state: FSMContext):
    game = await rq.get_game_by_id(3)
    user = await rq.get_user_by_tg_id(call.from_user.id)

    if not game or not user:
        await call.answer("❌ Ошибка загрузки данных", show_alert=True)
        return

    await state.set_state(DiceState.waiting_bet)
    await state.update_data(game_id=3, tg_id=call.from_user.id)

    await call.message.answer(
        f"🎲 Игра: Кости\n"
        f"💰 Баланс: {user.balance}\n"
        f"📌 Ставки: {game.min_bet}-{game.max_bet}\n\n"
        "Введите вашу ставку:"
    )
    await call.answer()

@play_dice_router.message(DiceState.waiting_bet, F.text)
async def process_bet(message: Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("❌ Введите число!")
        return

    bet = int(message.text)
    user_id = message.from_user.id
    data = await state.get_data()
    game = await rq.get_game_by_id(data['game_id'])
    user = await rq.get_user_by_tg_id(user_id)

    if not game or not user:
        await message.answer("❌ Ошибка данных")
        return
    if bet < game.min_bet:
        await message.answer(f"❌ Минимальная ставка: {game.min_bet}")
        return
    if bet > game.max_bet:
        await message.answer(f"❌ Максимальная ставка: {game.max_bet}")
        return
    if bet > user.balance:
        await message.answer("❌ Недостаточно средств")
        return

    await state.update_data(bet=bet)
    await state.set_state(DiceState.waiting_number)


    await message.answer(
        f"✅ Ставка {bet} принята!\nВыберите число:",
        reply_markup=await kb.dice_numbers()
    )

@play_dice_router.callback_query(DiceState.waiting_number, F.data.startswith("dice_num_"))
async def process_number(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    tg_id = call.from_user.id
    number = int(call.data.split("_")[2])
    dice_value, win = await DiceGame.roll(data['bet'], number)
    balance_change = win - data['bet']
    await rq.update_user_balance(tg_id, balance_change)
    user = await rq.get_user_by_tg_id(tg_id)
    result = (
        f"🎲 Ваше число: {number}\n"
        f"🎯 Выпало: {dice_value}\n\n"
        f"💰 {'Выиграли' if win > 0 else 'Проиграли'}: {abs(balance_change)}\n"
        f"💳 Новый баланс: {user.balance}"
    )
    await call.message.edit_text(result)
    await state.clear()
    await call.answer()