import random
from typing import Tuple

class DiceGame:
    @staticmethod
    async def roll(bet: int, number: int) -> Tuple[int, int]:
        dice_value = random.randint(1, 6)
        return dice_value, bet * 5 if dice_value == number else 0