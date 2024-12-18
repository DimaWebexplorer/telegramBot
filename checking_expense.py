from aiogram import Dispatcher
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.filters.state import StateFilter
from datetime import date, datetime
from bot import user_data, BudgetStates

async def check_balance(message: Message, state: FSMContext):
    user_id = message.from_user.id
    if (not user_data.user_exists(user_id)):
        await message.answer("Вы еще не зарегестрированы, пожалуйста начните /start")
        return
    
    await message.answer("Введите дату(в формате год-месяц-день), если хотите узгать траты за сегодня введите сегодня.")
    await state.set_state(BudgetStates.waiting_for_date)

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

def register_checking(dp: Dispatcher):
    dp.message.register(check_balance, Command(commands=['expense']))
    dp.message.register(process_balance, StateFilter(BudgetStates.waiting_for_date))