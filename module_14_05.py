import logging
from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from crud_functions import *
from aiogram.dispatcher.filters.state import State, StatesGroup
import requests
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

"""Config"""

api = ""

logging.basicConfig(level=logging.INFO)
bot = Bot(token=api)
dp = Dispatcher(bot, storage=MemoryStorage())

"""Клавиатуры"""

product_inline_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Product1", callback_data="product_buying")],
        [InlineKeyboardButton(text="Product2", callback_data="product_buying")],
        [InlineKeyboardButton(text="Product3", callback_data="product_buying")],
        [InlineKeyboardButton(text="Product4", callback_data="product_buying")]
    ], resize_keyboard=True
)

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
        [KeyboardButton(text="Купить")],
        [KeyboardButton(text="Регистрация")]
    ], resize_keyboard=True
)

"""Texts"""

formula_vesa = "10 х вес (кг) + 6,25 x рост (см) – 5 х возраст (г) + 5"
get_buying_list_text = "Название: {} | Описание: {} | Цена: {}"


def calculate_calories(age, growth, weight):
    norma = 10 * weight + 6.25 * growth - 5 * age + 5
    return norma


"""Классы"""


class UserState(StatesGroup):
    age = State()
    growth = State()
    weight = State()


class RegistrationState(StatesGroup):
    username = State()
    email = State()
    age = State()


"""Хэндлеры"""


@dp.message_handler(commands=['start'])
async def start(message):
    await message.answer("Привет! Я бот помогающий твоему здоровью", reply_markup=reply_kb)


"""Хэндлеры регистрации"""


@dp.message_handler(text='Регистрация')
async def sign_up(message):
    await message.answer('Введите имя пользователя (только латинский алфавит):')
    await RegistrationState.username.set()


@dp.message_handler(state=RegistrationState.username)
async def set_username(message, state):
    if not is_included(message.text):
        await state.update_data(username=message.text)
        await message.answer('Введите свой email:')
        await RegistrationState.email.set()
    else:
        await message.answer('Пользователь существует, введите другое имя')


@dp.message_handler(state=RegistrationState.email)
async def set_email(message, state):
    await state.update_data(email=message.text)
    await message.answer('Введите свой возраст:')
    await RegistrationState.age.set()


@dp.message_handler(state=RegistrationState.age)
async def set_age(message, state):
    await state.update_data(age=message.text)
    data = await state.get_data()
    username = data.get('username')
    email = data.get('email')
    age = data.get('age')
    add_user(username, email, age)
    await message.answer('Вы успешно зарегистрировались')
    await state.finish()


"""Остальные хэндлеры"""


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
    initiate_product_db()
    initiate_users_db()
    executor.start_polling(dp, skip_updates=True)
