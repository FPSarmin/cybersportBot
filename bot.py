from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.types.bot_command import BotCommand
import asyncio
from aiogram.dispatcher import FSMContext
import logging
from aiogram.utils.exceptions import BotBlocked
from SubscribingOnNews import register_subscribtion
from common import register_common
from users import users
from NewsGetter import news
from config import TOKEN
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
from suggestions import suggestions
from common import keyboard_base
from silent_mode import register_silent_mode

bot = Bot(token=TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())


class SayAllStatus(StatesGroup):
    waiting_for_message = State()


async def say_everyone(message: types.Message):
    if message.from_user.id == 506424401:
        await message.answer('Введите, что хотите отправить всем:',
                             reply_markup=types.ReplyKeyboardRemove())
        await SayAllStatus.waiting_for_message.set()
    else:
        await message.answer('Вы не имеете право изпользовать данную команду', reply_markup=keyboard_base)


async def say_everyone_get(message: types.Message, state: FSMContext):
    await state.update_data(mes=message.text)
    for user_id in users.get_users_ids():
        await bot.send_message(chat_id=user_id, text=message.text)
    await message.answer('Сообщения отправлены ' + str(len(users.get_users_ids())) + ' пользователям',
                         reply_markup=keyboard_base)


async def set_commands(b: Bot):
    commands = [
        BotCommand(command='/start', description='Начать знакомство'),
        BotCommand(command='/subscribe',
                   description='Подписаться/отписаться на/от новости(ей)'),
        BotCommand(command='/set_silent_mode',
                   description='Изменить время тихого режима')
    ]
    await b.set_my_commands(commands)


async def scheduled(wait_for):
    while True:
        await asyncio.sleep(wait_for)
        news.update()
        df = news.df[news.df.new == 1]
        for index, new in df.iterrows():
            try:
                indexes_match_queries = users.df.apply(
                    lambda row: row[new['news_type']] == 1,
                    axis=1
                )
                user_list = users.df[indexes_match_queries]
                for ind, ne in user_list.iterrows():
                    try:
                        await bot.send_message(user_list.loc[ind, 'user_id'], '<b>' + new['news_title'] + '</b>'
                                               + '\n\n' +
                                               new['news_description'] + '\n<a href="' +
                                               new['news_link'] + '">Читать далее...</a>' +
                                               '\n\n#' + new['news_type'],
                                               parse_mode="HTML",
                                               disable_web_page_preview=True,
                                               disable_notification=users.is_in_time(user_list.loc[ind, 'user_id']))
                    except BotBlocked:
                        users.remove_user(user_list.loc[ind, 'user_id'])
                        print(
                            f"Меня заблокировал пользователь! Удаляю его из базы данных\nОшибка: {BotBlocked}")
            except KeyError:
                suggestions.add_suggestion(
                    506424401, 'Добавьте игру ' + new['news_type'])
            news.change_news_status(new['news_link'])


async def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s"
    )
    logging.error("Starting Bot")

    register_common(dp)
    register_subscribtion(dp)
    register_silent_mode(dp)
    dp.register_message_handler(say_everyone, commands='sayall', state='*')
    dp.register_message_handler(
        say_everyone_get, state=SayAllStatus.waiting_for_message)

    await set_commands(bot)

    loop = asyncio.get_event_loop()
    loop.create_task(scheduled(10))
    await dp.start_polling()


if __name__ == '__main__':
    asyncio.run(main())
