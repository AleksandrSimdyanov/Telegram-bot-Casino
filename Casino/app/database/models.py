import os
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import String, ForeignKey, Integer, DateTime, Enum
from datetime import datetime
from dotenv import load_dotenv
from enum import Enum as PyEnum

load_dotenv()

engine = create_async_engine(url=os.getenv("SQL_URL"))
async_session = async_sessionmaker(engine)

class Base(AsyncAttrs, DeclarativeBase):
    pass

class TransactionType(PyEnum):
    DEPOSIT = "deposit"     # Пополнение баланса
    WITHDRAW = "withdraw"   # Вывод средств
    BET = "bet"             # Ставка в игре
    WIN = "win"             # Выигрыш
    BONUS = "bonus"         # Бонус (реферальный, промо)
    FINE = "fine"           # Штраф (за мошенничество)

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    tg_id: Mapped[int] = mapped_column(Integer)
    username: Mapped[str] = mapped_column(String(100))
    balance: Mapped[int] = mapped_column(Integer, default=1000)

class Appeal(Base):
    __tablename__ = "appeals"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(String(100))
    phone_number: Mapped[str] = mapped_column(String(100))
    question: Mapped[str] = mapped_column(String(1000))
    status: Mapped[str] = mapped_column(String(100))

class Game(Base):
    __tablename__ = "games"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50))
    min_bet: Mapped[int] = mapped_column(Integer)
    max_bet: Mapped[int] = mapped_column(Integer)


async def async_main():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)