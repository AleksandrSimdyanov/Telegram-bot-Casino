import random
from typing import List, Tuple, Dict


class Blackjack:
    # Карты и их значения
    CARDS = {
        "2": 2, "3": 3, "4": 4, "5": 5, "6": 6, "7": 7, "8": 8,
        "9": 9, "10": 10, "J": 10, "Q": 10, "K": 10, "A": 11
    }

    # Иконки карт для отображения
    CARD_ICONS = {
        "?": "🂠",  # Иконка рубашки карты
        "2": "🂢", "3": "🂣", "4": "🂤", "5": "🂥", "6": "🂦",
        "7": "🂧", "8": "🂨", "9": "🂩", "10": "🂪",
        "J": "🂫", "Q": "🂭", "K": "🂮", "A": "🂡"
    }

    @staticmethod
    def new_deck() -> List[str]:
        """Создает и тасует новую колоду"""
        deck = list(Blackjack.CARDS.keys()) * 4
        random.shuffle(deck)
        return deck

    @staticmethod
    def calculate_hand(hand: List[str]) -> int:
        """Подсчитывает сумму очков в руке с учетом тузов"""
        total = sum(Blackjack.CARDS[card] for card in hand)
        aces = hand.count("A")

        while total > 21 and aces > 0:
            total -= 10
            aces -= 1

        return total

    @staticmethod
    def format_hand(hand: List[str], hide_first: bool = False) -> str:
        """Форматирует карты для отображения"""
        if hide_first:
            return f"{Blackjack.CARD_ICONS['?']} " + " ".join(Blackjack.CARD_ICONS[card] for card in hand[1:])
        return " ".join(Blackjack.CARD_ICONS[card] for card in hand)

    @staticmethod
    async def deal_initial_hands(deck: List[str]) -> Tuple[List[str], List[str], List[str]]:
        """Раздает начальные карты"""
        player_hand = [deck.pop(), deck.pop()]
        dealer_hand = [deck.pop(), deck.pop()]
        return player_hand, dealer_hand, deck

    @staticmethod
    async def player_hit(hand: List[str], deck: List[str]) -> Tuple[List[str], int, bool]:
        """Игрок берет карту"""
        hand.append(deck.pop())
        total = Blackjack.calculate_hand(hand)
        busted = total > 21
        return hand, total, busted

    @staticmethod
    async def dealer_play(dealer_hand: List[str], deck: List[str]) -> Tuple[List[str], int]:
        """Дилер добирает карты по правилам"""
        total = Blackjack.calculate_hand(dealer_hand)

        while total < 17:
            dealer_hand.append(deck.pop())
            total = Blackjack.calculate_hand(dealer_hand)

        return dealer_hand, total

    @staticmethod
    async def determine_winner(player_total: int, dealer_total: int, bet: int) -> Tuple[int, str]:
        """Определяет результат игры"""
        if player_total > 21:
            return -bet, "Перебор! Вы проиграли 💸"
        elif dealer_total > 21:
            return bet, "Дилер перебрал! Вы выиграли 🎉"
        elif player_total > dealer_total:
            return bet, f"{player_total} > {dealer_total}. Вы выиграли 🎉"
        elif player_total < dealer_total:
            return -bet, f"{player_total} < {dealer_total}. Вы проиграли 💸"
        else:
            return 0, "Ничья 🤝"