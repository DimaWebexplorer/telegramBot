from aiogram import Dispatcher
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.filters.state import StateFilter
from datetime import date, datetime
from bot import user_data, BudgetStates

async def add_transaction(message: Message, state: FSMContext):
    await message.answer("Введите сумму и дату(в формате год-месяц-день), если хотите добавить платеж сегодня введите только сумму.")
    await state.set_state(BudgetStates.waiting_for_transaction)

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

def register_adding(dp: Dispatcher):
    dp.message.register(add_transaction, Command(commands=["add"]))
    dp.message.register(process_transaction, StateFilter(BudgetStates.waiting_for_transaction))