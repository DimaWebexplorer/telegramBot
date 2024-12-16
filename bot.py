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

@dp.message(Command(commands=['add']))
async def add_transaction(message: Message, state: FSMContext):
    await message.answer("Введите сумму и дату(в формате год-месяц-день), если хотите добавить платеж сегодня введите только сумму.")
    await state.set_state(BudgetStates.waiting_for_transaction)

@dp.message(StateFilter(BudgetStates.waiting_for_transaction))
async def process_transaction(message: Message, state: FSMContext):
    user_id = message.from_user.id
    if (not user_data.user_exists(user_id)):
        await message.answer("Вы еще не зарегестрированы, пожалуйста начните /start")
        return

    parts = message.text.split(" ")
    payment_date = date.today().strftime("%Y-%m-%d")
    
    if (len(parts) == 2):
        try:
            payment_date = datetime.strptime(parts[1], "%Y-%m-%d").strftime("%Y-%m-%d")
        except ValueError:
            await message.answer("Неверный формат даты!")
            return
    payment = 0
    
    try:
        payment = float(parts[0])
    except ValueError:
        await message.answer("Неверный формат суммы!")
    
    if (user_data.record_exists(user_id, payment_date)):
        payment += user_data.get_record(user_id, payment_date)
        user_data.update_balance(user_id, payment, payment_date)
    else:
        user_data.add_balance(user_id, payment, payment_date)

    await state.clear()

@dp.message(Command(commands=['expense']))
async def check_balance(message: Message, state: FSMContext):
    user_id = message.from_user.id
    if (not user_data.user_exists(user_id)):
        await message.answer("Вы еще не зарегестрированы, пожалуйста начните /start")
        return
    
    await message.answer("Введите дату(в формате год-месяц-день), если хотите узгать траты за сегодня введите сегодня.")
    await state.set_state(BudgetStates.waiting_for_date)

@dp.message(StateFilter(BudgetStates.waiting_for_date))
async def process_balance(message: Message, state: FSMContext):
    user_id = message.from_user.id
    if (not user_data.user_exists(user_id)):
        await message.answer("Вы еще не зарегестрированы, пожалуйста начните /start")
        return

    payment_date = date.today().strftime("%Y-%m-%d")
    if (message.text != "сегодня" and message.text != "Сегодня" ):
        try:
            payment_date = datetime.strptime(message.text, "%Y-%m-%d").strftime("%Y-%m-%d")
        except ValueError:
            await message.answer("Неверный формат даты!")
            return
    
    await message.answer(f"Траты на {payment_date} - {user_data.get_record(user_id, payment_date)} рублей")
    state.clear()

@dp.message(Command(commands=['expenses_statistics']))
async def list_transactions(message: Message, state: FSMContext):
    user_id = message.from_user.id
    if (not user_data.user_exists(user_id)):
        await message.answer("Вы еще не зарегестрированы, пожалуйста начните /start")
        return
    
    await message.answer("Введите период для отобраения статистики трат по нему: количество дней, или все для отображения всех трат.")
    await state.set_state(BudgetStates.waiting_for_period)

@dp.message(StateFilter(BudgetStates.waiting_for_period))
async def process_transactions(message: Message, state: FSMContext):
    user_id = message.from_user.id
    response = "Ваши траты:\n"
    list_transactions = []
    if (message.text == "все" or message.text == "Все"):
        list_transactions = user_data.extract_all_data(user_id)
    else:
        days = 0
        try:
            days = int(message.text)
        except ValueError:
            await message.answer("Неверный формат!")
        end = date.today().strftime("%Y-%m-%d")
        start = (date.today() - timedelta(days=days)).strftime("%Y-%m-%d")
        list_transactions = user_data.extract_data(user_id, start, end)

    for (payment, payment_date) in list_transactions:
        response += f"Траты на {payment_date} - {payment}\n"

    await message.answer(response)
    state.clear()

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
