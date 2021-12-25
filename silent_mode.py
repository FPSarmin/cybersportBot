from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher.filters.builtin import Text
from users import users
from common import keyboard_base


class ChoosingSilent(StatesGroup):
    waiting_for_time_begin = State()
    waiting_for_time_end = State()


times = list(range(24))
keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
for time in times:
    keyboard.add(str(time).rjust(2, '0'))
keyboard.add('Назад')


async def choosing_time_start(message: types.Message):
    await message.answer('Выберите час начиная с которого вы хотите получать сообщения в тихом режиме',
                         reply_markup=keyboard)
    await ChoosingSilent.waiting_for_time_begin.set()


async def choosing_begin_time(message: types.Message, state: FSMContext):
    if int(message.text.lstrip('0').rjust(1, '0')) not in times:
        await message.answer('Пожалуйста, выберите время из списка')
        return
    await state.update_data(silent_begin=int(message.text.lstrip('0').rjust(1, '0')))
    users.change_silent_begin(message.from_user.id, int(
        message.text.lstrip('0').rjust(1, '0')))
    await message.answer('Время начала изменено, теперь введите время конца тихого режима', reply_markup=keyboard)
    await ChoosingSilent.next()


async def choosing_end_time(message: types.Message, state: FSMContext):
    time_begin = await state.get_data()
    if int(message.text.lstrip('0').rjust(1, '0')) not in times:
        await message.answer('Пожалуйста, выберите время из списка')
        return
    if int(message.text.lstrip('0').rjust(1, '0')) == time_begin['silent_begin']:
        await message.answer('Вы не можете вечно сидеть в тишине :)\nЕсли хотите, можете замьютить бота\n'
                             'Но лучше выберите другое время конца')
        return
    await state.update_data(silent_end=int(message.text.lstrip('0').rjust(1, '0')))
    users.change_silent_end(message.from_user.id, int(
        message.text.lstrip('0').rjust(1, '0')))
    await message.answer('Время конца изменено, теперь в этот период вы будете получать сообщения в беззвучном режиме',
                         reply_markup=keyboard_base)
    await state.finish()
    return


def register_silent_mode(dp: Dispatcher):
    dp.register_message_handler(
        choosing_time_start, commands='set_silent_mode', state='*')
    dp.register_message_handler(choosing_time_start, Text(
        equals='Настроить тихий режим'), state='*')
    dp.register_message_handler(
        choosing_begin_time, state=ChoosingSilent.waiting_for_time_begin)
    dp.register_message_handler(
        choosing_end_time, state=ChoosingSilent.waiting_for_time_end)
