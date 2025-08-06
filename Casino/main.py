import os
from aiogram import Bot, Dispatcher
import asyncio
from app.database.models import async_main
from dotenv import load_dotenv
from app.handlers.user_handler import user_router
from app.states.registered_user import reg_user_router
from app.states.play_dice import play_dice_router
from app.states.play_roulette import play_roulette_router
from app.states.play_blackjack import play_blackjack_router
from app.states.do_appeal import do_appeal_router

load_dotenv()
bot = Bot(os.getenv("TOKEN"))
dp = Dispatcher()

async def main():
    await async_main()
    dp.include_routers(user_router,
                       reg_user_router,
                       play_dice_router,
                       play_roulette_router,
                       play_blackjack_router,
                       do_appeal_router)
    await dp.start_polling(bot)
if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Бот выключен")