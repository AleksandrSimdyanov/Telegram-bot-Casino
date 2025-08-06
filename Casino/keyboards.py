from aiogram.types import (InlineKeyboardButton,
                           InlineKeyboardMarkup,
                           ReplyKeyboardMarkup,
                           KeyboardButton)
from aiogram.utils.keyboard import InlineKeyboardBuilder
import app.database.requests as rq

start_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Игры"), KeyboardButton(text="Баланс")],
        [KeyboardButton(text="Помощь")]
    ], resize_keyboard=True
)

async def games_kb(back=True):
    builder = InlineKeyboardBuilder()
    games = await rq.get_all_games()
    for game in games:
        button = InlineKeyboardButton(text=game.name, callback_data=f"game_{game.id}")
        builder.add(button)
    if back:
        builder.row(InlineKeyboardButton(text="⏪Вернуться", callback_data="back_menu"))
    return builder.as_markup()

async def dice_numbers():
    builder = InlineKeyboardBuilder()
    for number in range(1, 7):
        button = InlineKeyboardButton(text=str(number), callback_data=f"dice_num_{number}")
        builder.add(button)
    builder.adjust(3, 3)
    return builder.as_markup()

async def get_bet_keyboard():
    """Клавиатура для выбора ставки"""
    builder = InlineKeyboardBuilder()
    builder.button(text="10 🪙", callback_data="roulette_bet_10")
    builder.button(text="50 🪙", callback_data="roulette_bet_50")
    builder.button(text="100 🪙", callback_data="roulette_bet_100")
    builder.button(text="500 🪙", callback_data="roulette_bet_500")
    builder.button(text="❌ Отмена", callback_data="roulette_cancel")
    builder.adjust(2, 2, 1)
    return builder.as_markup()

async def roulette_kb():
    builder = InlineKeyboardBuilder()
    builder.button(text="🎰 Крутить рулетку", callback_data="roulette_spin")
    builder.button(text="❌ Отмена", callback_data="roulette_cancel")
    return builder.as_markup()

async def blackjack_kb():
    builder = InlineKeyboardBuilder()
    builder.button(text="Начать блекджек", callback_data="blackjack_start")
    builder.button(text="❌ Отмена", callback_data="blackjack_cancel")
    return builder.as_markup()

async def blackjack_bet_keyboard():
    builder = InlineKeyboardBuilder()
    builder.button(text="10 🪙", callback_data="bj_bet_10")
    builder.button(text="50 🪙", callback_data="bj_bet_50")
    builder.button(text="100 🪙", callback_data="bj_bet_100")
    builder.button(text="500 🪙", callback_data="bj_bet_500")
    builder.button(text="❌ Отмена", callback_data="bj_cancel")
    builder.adjust(2, 2, 1)
    return builder.as_markup()

async def blackjack_action_keyboard(can_double: bool = True):
    builder = InlineKeyboardBuilder()
    builder.button(text="✅ Взять карту", callback_data="bj_hit")
    builder.button(text="✋ Остановиться", callback_data="bj_stand")
    if can_double:
        builder.button(text="💰 Удвоить", callback_data="bj_double")
    builder.button(text="❌ Сдаться", callback_data="bj_surrender")
    builder.adjust(2, 2)
    return builder.as_markup()

phone_number_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Контакт", request_contact=True)]
    ], resize_keyboard=True
)

yes_no_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Да"), KeyboardButton(text="Нет")]
    ], resize_keyboard=True
)