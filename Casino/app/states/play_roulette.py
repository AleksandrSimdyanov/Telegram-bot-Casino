from aiogram import F, Router
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
import app.database.requests as rq
import keyboards as kb
import random
from typing import Optional, Tuple
from app.database.models import User, Game
from Games.Roulette import RouletteGame

play_roulette_router = Router()


class RouletteState(StatesGroup):
    waiting_bet = State()
    waiting_spin = State()


@play_roulette_router.callback_query(F.data == "game_2")
async def start_roulette(call: CallbackQuery, state: FSMContext):
    game = await rq.get_game_by_id(2)
    user = await rq.get_user_by_tg_id(call.from_user.id)

    if not game or not user:
        await call.answer("❌ Ошибка загрузки данных", show_alert=True)
        return

    await state.set_state(RouletteState.waiting_bet)
    await state.update_data(game_id=2, tg_id=call.from_user.id)

    await call.message.answer(
        f"🎰 Фруктовая Рулетка\n"
        f"💰 Баланс: {user.balance}\n"
        f"📌 Ставки: {game.min_bet}-{game.max_bet}\n\n"
        "Введите вашу ставку:",
    )
    await call.answer()

@play_roulette_router.message(RouletteState.waiting_bet, F.text)
async def process_bet(message: Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("❌ Введите число!")
        return

    bet = int(message.text)
    data = await state.get_data()
    game = await rq.get_game_by_id(data['game_id'])
    user = await rq.get_user_by_tg_id(data['tg_id'])

    # Валидация ставки
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
    await state.set_state(RouletteState.waiting_spin)

    await message.answer(
        f"✅ Ставка {bet} принята!\n"
        "Нажмите кнопку, чтобы крутить рулетку:",
        reply_markup=await kb.roulette_kb()
    )

@play_roulette_router.callback_query(RouletteState.waiting_spin, F.data == "roulette_spin")
async def spin_roulette(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    bet = data['bet']
    tg_id = data['tg_id']

    # Крутим рулетку
    wheel, win_amount, result_text = await RouletteGame.spin(bet)

    # Обновляем баланс
    user = await rq.update_user_balance(tg_id, win_amount - bet)

    # Формируем результат
    wheel_text = "\n".join([" | ".join(row) for row in wheel])
    result = (
        f"🎰 Результаты:\n\n"
        f"{wheel_text}\n\n"
        f"{result_text}\n"
        f"💰 Итоговый выигрыш: {win_amount}\n"
        f"💳 Новый баланс: {user.balance}"
    )

    await call.message.edit_text(result)
    await state.clear()
    await call.answer()

@play_roulette_router.callback_query(F.data == "roulette_cancel")
async def cancel_roulette(call: CallbackQuery, state: FSMContext):
    await state.clear()
    await call.message.edit_text("❌ Игра отменена")
    await call.answer()


