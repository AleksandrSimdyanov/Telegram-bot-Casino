import random
from typing import Tuple, List

class RouletteGame:
    FRUITS = {
        "🍒": {"name": "Вишня", "multiplier": 1.5},
        "🍊": {"name": "Апельсин", "multiplier": 2},
        "🍋": {"name": "Лимон", "multiplier": 3},
        "🍇": {"name": "Виноград", "multiplier": 5},
        "🍉": {"name": "Арбуз", "multiplier": 7},
        "🍓": {"name": "Клубника", "multiplier": 10},
        "7️⃣": {"name": "Семерка", "multiplier": 20}
    }

    @staticmethod
    async def spin(bet: int):
        symbols = list(RouletteGame.FRUITS.keys())
        wheel = [
            [random.choice(symbols) for _ in range(3)],
            [random.choice(symbols) for _ in range(3)],
            [random.choice(symbols) for _ in range(3)]
        ]
        win_amount = 0
        result_text = ""

        for i, row in enumerate(wheel):
            if len(set(row)) == 1:
                fruit = row[0]
                multiplier = RouletteGame.FRUITS[fruit]["multiplier"]
                line_win = int(bet * multiplier)
                win_amount += line_win
                result_text += f"Линия {i + 1}: {fruit * 3} x{multiplier}\n"

        for col in range(3):
            column = [wheel[0][col], wheel[1][col], wheel[2][col]]
            if len(set(column)) == 1:
                fruit = column[0]
                multiplier = RouletteGame.FRUITS[fruit]["multiplier"]
                line_win = int(bet * multiplier)
                win_amount += line_win
                result_text += f"Колонка {col + 1}: {fruit * 3} ×{multiplier}\n"

            # Проверяем диагонали
        diag1 = [wheel[0][0], wheel[1][1], wheel[2][2]]
        diag2 = [wheel[0][2], wheel[1][1], wheel[2][0]]

        for i, diag in enumerate([diag1, diag2]):
            if len(set(diag)) == 1:
                fruit = diag[0]
                multiplier = RouletteGame.FRUITS[fruit]["multiplier"]
                line_win = int(bet * multiplier)
                win_amount += line_win
                result_text += f"Диагональ {i + 1}: {fruit * 3} ×{multiplier}\n"

        if not result_text:
            result_text = "Нет выигрышных линий 😢"

        return wheel, win_amount, result_text

    @staticmethod
    def format_wheel(wheel: List[List[str]]) -> str:
        """Форматируем колесо для вывода"""
        return "\n".join([" | ".join(row) for row in wheel])