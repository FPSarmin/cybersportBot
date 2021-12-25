from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.builtin import Text
from aiogram.dispatcher.filters.state import State, StatesGroup
from users import users
from suggestions import suggestions

keyboard_base = types.ReplyKeyboardMarkup(resize_keyboard=True)
keyboard_base.add('Подписаться/отписаться на/от новости(ей)')
keyboard_base.add('Добавить предложение или отзыв')
keyboard_base.add('Настроить тихий режим')


class SuggestionStatus(StatesGroup):
    waiting_for_suggestion = State()


async def start(message: types.Message, state: FSMContext):
    await state.finish()
    print(message.from_user.id)
    if not users.find_user(message.from_user.id):
        users.add_user(message.from_user.id)
    await message.answer("Добро пожаловать! Выберите что хотите сделать в меню ниже",
                         reply_markup=keyboard_base)


async def cancel(message: types.Message, state: FSMContext):
    await state.finish()
    print(message.from_user.id)
    await message.answer('Вы вернулись к началу', reply_markup=keyboard_base)


async def suggestion_add(message: types.Message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add("Отмена")
    await message.answer('Введите ваше предложение или отзыв. Или введите "отмена",'
                         ' если отпало желание или случайно нажали на этот пункт',
                         reply_markup=keyboard)
    await SuggestionStatus.waiting_for_suggestion.set()


async def suggestion_get(message: types.Message, state: FSMContext):
    await state.update_data(suggestion=message.text)
    suggestions.add_suggestion(message.from_user.id, message.text)
    await message.answer('Огромное спасибо за ваше обращение!', reply_markup=keyboard_base)
    await state.finish()


def register_common(dp: Dispatcher):
    dp.register_message_handler(start, commands='start', state='*')
    dp.register_message_handler(cancel, commands='cancel', state='*')
    dp.register_message_handler(cancel, Text(
        equals='назад', ignore_case=True), state='*')
    dp.register_message_handler(cancel, Text(
        equals='отмена', ignore_case=True), state='*')
    dp.register_message_handler(suggestion_add, Text(
        equals='Добавить предложение или отзыв'), state='*')
    dp.register_message_handler(
        suggestion_get, state=SuggestionStatus.waiting_for_suggestion)
