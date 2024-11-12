import logging

from crud_functions import *
import requests
from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

api = ""

formula_vesa = "10 х вес (кг) + 6,25 x рост (см) – 5 х возраст (г) + 5"
get_buying_list_text = "Название: {} | Описание: {} | Цена: {}"

logging.basicConfig(level=logging.INFO)
bot = Bot(token=api)
dp = Dispatcher(bot, storage=MemoryStorage())

"""
Новая клавиатура к заданию 'Доработка бота'
"""

product_inline_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Product1", callback_data="product_buying")],
        [InlineKeyboardButton(text="Product2", callback_data="product_buying")],
        [InlineKeyboardButton(text="Product3", callback_data="product_buying")],
        [InlineKeyboardButton(text="Product4", callback_data="product_buying")]
    ], resize_keyboard=True
)

"""
Клавиатуры со старых заданий
"""

inline_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Рассчитать норму калорий", callback_data="calories")],
        [InlineKeyboardButton(text="Формулы расчёта", callback_data="formulas")]
    ], resize_keyboard=True
)

reply_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Рассчитать")],
        [KeyboardButton(text="Информация")],
        [KeyboardButton(text="Купить")]
    ], resize_keyboard=True
)


def calculate_calories(age, growth, weight):
    norma = 10 * weight + 6.25 * growth - 5 * age + 5
    return norma


class UserState(StatesGroup):
    age = State()
    growth = State()
    weight = State()


@dp.message_handler(commands=['start'])
async def start(message):
    await message.answer("Привет! Я бот помогающий твоему здоровью", reply_markup=reply_kb)

"""
Хэндлеры и функции по заданию 'Доработка бота' 
"""


@dp.message_handler(text="Купить")
async def get_buying_list(message):
    products = get_all_products()
    for product in products:
        await message.answer(get_buying_list_text.format(product[1], product[2], product[3]))
        response = requests.get(product[4], stream=True)
        response.raise_for_status()
        await message.answer_photo(photo=response.raw)
    await message.answer('Выберите продукт для покупки:', reply_markup=product_inline_kb)


@dp.callback_query_handler(text='product_buying')
async def send_confirm_message(call):
    await call.message.answer('Вы успешно приобрели продукт!')
    await call.answer()


"""
Остальные хэндлеры и функции с прошлых заданий
"""


@dp.message_handler(text="Рассчитать")
async def main_menu(message):
    await message.answer('Выберите опцию:', reply_markup=inline_kb)


@dp.callback_query_handler(text="formulas")
async def get_formulas(call):
    await call.message.answer(formula_vesa)


@dp.callback_query_handler(text='calories')
async def set_age(call):
    await call.message.answer('Введите ваш возраст')
    await UserState.age.set()
    await call.answer()


@dp.message_handler(state=UserState.age)
async def set_growth(message, state):
    await state.update_data(age=message.text)
    await message.answer('Введите ваш рост')
    await UserState.growth.set()


@dp.message_handler(state=UserState.growth)
async def set_weight(message, state):
    await state.update_data(growth=message.text)
    await message.answer('Введите ваш вес')
    await UserState.weight.set()


@dp.message_handler(state=UserState.weight)
async def send_calories(message, state):
    await state.update_data(weight=message.text)
    data = await state.get_data()
    age = int(data.get('age'))
    growth = int(data.get('growth'))
    weight = int(data.get('weight'))
    calories = calculate_calories(age, growth, weight)
    await message.answer(f'Ваша норма калорий - {calories} ккал')
    await state.finish()


@dp.message_handler()
async def all_messages(message):
    await message.answer('Введите команду /start, чтобы начать общение')


if __name__ == '__main__':
    initiate_db()
    executor.start_polling(dp, skip_updates=True)
