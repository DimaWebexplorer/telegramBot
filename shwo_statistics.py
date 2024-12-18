from aiogram import Dispatcher
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.filters.state import StateFilter
from datetime import date, datetime, timedelta
from bot import user_data, BudgetStates

async def list_transactions(message: Message, state: FSMContext):
    user_id = message.from_user.id
    if (not user_data.user_exists(user_id)):
        await message.answer("Вы еще не зарегестрированы, пожалуйста начните /start")
        return
    
    await message.answer("Введите период для отобраения статистики трат по нему: количество дней, или все для отображения всех трат.")
    await state.set_state(BudgetStates.waiting_for_period)


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

def register_statistics(dp: Dispatcher):
    dp.message.register(list_transactions, Command(commands=['expenses_statistics']))
    dp.message.register(process_transactions, StateFilter(BudgetStates.waiting_for_period))