from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher.filters.builtin import Text
from users import users


class SubscribingNews(StatesGroup):
    waiting_for_choosing = State()


games = {'Dota 2': 'dota2', 'CS-GO': 'cs-go', 'PUBG': 'pubg', 'Общие новости про игры': 'games',
         'Прочие новости': 'others', 'LOL': 'lol', 'Valorant': 'valorant', "Apex Legends": 'apex-legends',
         'FIFA': 'fifa', 'Overwatch': 'overwatch', 'Fortnite': 'fortnite'}


async def subscribing_start(message: types.Message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for key in games:
        keyboard.add(key)
    keyboard.add('Назад')
    await message.answer('На какие новости вы хотите подписаться/отписаться?', reply_markup=keyboard)
    await SubscribingNews.waiting_for_choosing.set()


async def subscribing_set(message: types.Message, state: FSMContext):
    if message.text not in games:
        await message.answer("Пожалуйста выберите тип новостей используя клавиатуру ниже")
        return
    await state.update_data(chosen_game=message.text)
    users.subscribe_user(message.from_user.id, games[message.text])
    if users.get_sub_status(message.from_user.id, games[message.text]) == 1:
        await message.answer("Вы успешно подписались на рассылку на " + message.text)
    else:
        await message.answer("Вы успешно отписались от рассылки на " + message.text)
    return


def register_subscribtion(dp: Dispatcher):
    dp.register_message_handler(subscribing_start, commands='subscribe', state='*')
    dp.register_message_handler(subscribing_start, Text(equals='Подписаться/отписаться на/от новости(ей)'), state='*')
    dp.register_message_handler(subscribing_set, state=SubscribingNews.waiting_for_choosing)
