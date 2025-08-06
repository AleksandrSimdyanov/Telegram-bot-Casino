from aiogram import F, Router
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder
import app.database.requests as rq
from Games.Blackjack import Blackjack

play_blackjack_router = Router()


class BlackjackState(StatesGroup):
    waiting_bet = State()
    playing = State()


async def get_blackjack_keyboard(can_double: bool = True) -> InlineKeyboardBuilder:
    """Создает клавиатуру для игры"""
    builder = InlineKeyboardBuilder()
    builder.button(text="✅ Взять карту", callback_data="bj_hit")
    builder.button(text="✋ Остановиться", callback_data="bj_stand")
    if can_double:
        builder.button(text="💰 Удвоить", callback_data="bj_double")
    builder.button(text="❌ Сдаться", callback_data="bj_surrender")
    builder.adjust(2)
    return builder


@play_blackjack_router.callback_query(F.data == "game_1")
async def start_blackjack(call: CallbackQuery, state: FSMContext):
    try:
        game = await rq.get_game_by_id(1)
        user = await rq.get_user_by_tg_id(call.from_user.id)

        if not game or not user:
            await call.answer("❌ Ошибка загрузки данных", show_alert=True)
            return

        await state.set_state(BlackjackState.waiting_bet)
        await state.update_data(game_id=1, tg_id=call.from_user.id)

        await call.message.answer(
            f"🃏 Блэкджек (21)\n"
            f"💰 Баланс: {user.balance}\n"
            f"📌 Ставки: {game.min_bet}-{game.max_bet}\n\n"
            "Введите вашу ставку:"
        )
        await call.answer()
    except Exception as e:
        await call.answer("⚠️ Ошибка сервера", show_alert=True)
        await state.clear()


@play_blackjack_router.message(BlackjackState.waiting_bet, F.text)
async def process_bet(message: Message, state: FSMContext):
    try:
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

        # Создаем новую колоду и раздаем карты
        deck = Blackjack.new_deck()
        player_hand, dealer_hand, deck = await Blackjack.deal_initial_hands(deck)
        player_sum = Blackjack.calculate_hand(player_hand)
        dealer_sum = Blackjack.calculate_hand(dealer_hand)

        # Проверяем блэкджек
        blackjack = player_sum == 21
        can_double = True  # Удвоение доступно только при первых двух картах

        # Сохраняем состояние
        await state.update_data(
            bet=bet,
            player_hand=player_hand,
            dealer_hand=dealer_hand,
            player_sum=player_sum,
            dealer_sum=dealer_sum,
            deck=deck,
            can_double=can_double
        )

        await state.set_state(BlackjackState.playing)

        if blackjack:
            await finish_blackjack_game(message, state, blackjack=True)
        else:
            keyboard = await get_blackjack_keyboard(can_double)
            await message.answer(
                f"Ваши карты: {Blackjack.format_hand(player_hand)}\n"
                f"Сумма: {player_sum}\n\n"
                f"Карты дилера: {Blackjack.format_hand(dealer_hand, hide_first=True)}\n\n"
                "Выберите действие:",
                reply_markup=keyboard.as_markup()
            )

    except Exception as e:
        await message.answer(f"⚠️ Ошибка: {str(e)}")
        await state.clear()


async def finish_blackjack_game(update: Message | CallbackQuery, state: FSMContext, blackjack: bool = False):
    """Завершает игру и показывает результаты"""
    data = await state.get_data()
    player_hand = data['player_hand']
    dealer_hand = data['dealer_hand']
    bet = data['bet']

    # Если это не блэкджек, дилер добирает карты
    if not blackjack:
        dealer_hand, dealer_sum = await Blackjack.dealer_play(dealer_hand, data['deck'])
    else:
        dealer_sum = Blackjack.calculate_hand(dealer_hand)

    player_sum = Blackjack.calculate_hand(player_hand)

    # Определяем результат
    win_amount, result_text = await Blackjack.determine_winner(
        player_sum, dealer_sum, bet
    )

    # Обновляем баланс
    user = await rq.update_user_balance(data['tg_id'], win_amount)

    # Формируем сообщение
    message_text = (
        f"🃏 Игра завершена!\n\n"
        f"Ваши карты: {Blackjack.format_hand(player_hand)}\n"
        f"Ваша сумма: {player_sum}\n\n"
        f"Карты дилера: {Blackjack.format_hand(dealer_hand)}\n"
        f"Сумма дилера: {dealer_sum}\n\n"
        f"{result_text}\n"
        f"💰 Изменение баланса: {'+' if win_amount > 0 else ''}{win_amount}\n"
        f"💳 Новый баланс: {user.balance}"
    )

    if isinstance(update, Message):
        await update.answer(message_text)
    else:
        await update.message.edit_text(message_text)

    await state.clear()


@play_blackjack_router.callback_query(BlackjackState.playing, F.data == "bj_hit")
async def hit_action(call: CallbackQuery, state: FSMContext):
    try:
        data = await state.get_data()
        player_hand, player_sum, deck = data['player_hand'], data['player_sum'], data['deck']

        # Игрок берет карту
        player_hand, player_sum, busted = await Blackjack.player_hit(player_hand, deck)

        # Обновляем состояние
        await state.update_data(
            player_hand=player_hand,
            player_sum=player_sum,
            can_double=False  # После взятия карты удвоение недоступно
        )

        if busted:
            await finish_blackjack_game(call, state)
        else:
            keyboard = await get_blackjack_keyboard(can_double=False)
            await call.message.edit_text(
                f"Ваши карты: {Blackjack.format_hand(player_hand)}\n"
                f"Сумма: {player_sum}\n\n"
                f"Карты дилера: {Blackjack.format_hand(data['dealer_hand'], hide_first=True)}\n\n"
                "Выберите действие:",
                reply_markup=keyboard.as_markup()
            )
        await call.answer()
    except Exception as e:
        await call.answer(f"⚠️ Ошибка: {str(e)}", show_alert=True)


@play_blackjack_router.callback_query(BlackjackState.playing, F.data == "bj_stand")
async def stand_action(call: CallbackQuery, state: FSMContext):
    await finish_blackjack_game(call, state)
    await call.answer()


@play_blackjack_router.callback_query(BlackjackState.playing, F.data == "bj_double")
async def double_action(call: CallbackQuery, state: FSMContext):
    try:
        data = await state.get_data()
        user = await rq.get_user_by_tg_id(data['tg_id'])

        # Проверяем возможность удвоения
        if data['bet'] * 2 > user.balance:
            await call.answer("❌ Недостаточно средств для удвоения", show_alert=True)
            return

        # Удваиваем ставку
        await state.update_data(bet=data['bet'] * 2)

        # Игрок берет одну карту и автоматически останавливается
        player_hand, player_sum, _ = await Blackjack.player_hit(data['player_hand'], data['deck'])
        await state.update_data(player_hand=player_hand, player_sum=player_sum)

        await finish_blackjack_game(call, state)
        await call.answer("💰 Ставка удвоена")
    except Exception as e:
        await call.answer(f"⚠️ Ошибка: {str(e)}", show_alert=True)


@play_blackjack_router.callback_query(BlackjackState.playing, F.data == "bj_surrender")
async def surrender_action(call: CallbackQuery, state: FSMContext):
    try:
        data = await state.get_data()
        surrender_amount = -data['bet'] // 2  # Возвращаем половину ставки

        # Обновляем баланс
        user = await rq.update_user_balance(data['tg_id'], surrender_amount)

        await call.message.edit_text(
            f"🃏 Вы сдались!\n"
            f"💰 Возвращено: {abs(surrender_amount)}\n"
            f"💳 Новый баланс: {user.balance}"
        )
        await state.clear()
        await call.answer()
    except Exception as e:
        await call.answer(f"⚠️ Ошибка: {str(e)}", show_alert=True)
