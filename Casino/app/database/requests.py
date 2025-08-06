from app.database.models import User, Game, async_session
from sqlalchemy import select
from app.database.models import Appeal

# действия с играми
async def get_all_games():
    async with async_session() as session:
        return await session.scalars(select(Game))

async def get_game_by_id(game_id):
    async with async_session() as session:
        return await session.scalar(select(Game).where(Game.id == game_id))

async def get_game_by_name(name):
    async with async_session() as session:
        return await session.scalar(select(Game).where(Game.name == name))

# действия с пользователями
async def add_user(username, tg_id):
    async with async_session() as session:
        user = User(username=username,
                    tg_id=tg_id)
        session.add(user)
        await session.commit()

async def get_user_by_tg_id(tg_id):
    async with async_session() as session:
        return await session.scalar(select(User).where(User.tg_id == tg_id))


async def update_user_balance(user_id: int, amount: int) -> User:
    async with async_session() as session:
        # Получаем пользователя с блокировкой для обновления
        result = await session.execute(
            select(User)
            .where(User.tg_id == user_id)
            .with_for_update()  # Важно для избежания race condition
        )
        user = result.scalar_one_or_none()

        if not user:
            raise ValueError(f"User with tg_id {user_id} not found")

        # Обновляем баланс
        user.balance += amount

        try:
            await session.commit()
            await session.refresh(user)  # Получаем актуальные данные
            return user
        except Exception as e:
            await session.rollback()
            raise ValueError(f"Balance update failed: {str(e)}")

async def add_question(user_id, question, status, phone_number = None):
    async with async_session() as session:
        appeal = Appeal(user_id=user_id, question=question, status=status, phone_number=phone_number)
        session.add(appeal)
        await session.commit()