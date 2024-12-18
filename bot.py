import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.filters.state import StateFilter
from aiogram.filters.command import CommandStart
import sys
import asyncio
from datetime import date, datetime, timedelta
from db_work import BudgetTracker

API_TOKEN = '7644760442:AAGJEeCp86QcGtIe7isYqY1XGwLmw5NhvSI'

logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)
user_data = BudgetTracker('budget_tracker.db')

class BudgetStates(StatesGroup):
    waiting_for_transaction = State()
    waiting_for_date = State()
    waiting_for_period = State()

@dp.message(CommandStart())
async def send_welcome(message: Message):
    if (not user_data.user_exists(message.from_user.id)):
        user_data.create_user_table(message.from_user.id)
        await message.answer(f"Добро пожаловать, {message.from_user.username}!\nДля добавления трат используйте /add, для провекри трат используйте /expense, для вывода статистики трат используйте /expenses_statistics.")
    else:
        await message.answer(f"С возвращением, {message.from_user.username}!")

async def main():
    from adding_expense import register_adding
    from checking_expense import register_checking
    from shwo_statistics import register_statistics
    register_adding(dp)
    register_checking(dp)
    register_statistics(dp)
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
