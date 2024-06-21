from dotenv import load_dotenv
import os
from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.dispatcher.storage import FSMContext
import time
import re
import hashlib

import start_bd
from base.models import Client, Follow, Subject
from _mes import srd_message, DICT_MES
from markup import permission_markup, follow_inlinemarkup


load_dotenv()
BOT_TOKEN = os.getenv('BOT_TOKEN')
bot = Bot(BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)


class WriteJoke(StatesGroup):
    write = State()

class EditJoke(StatesGroup):
    edite = State()
    
# Принимает фото
@dp.message_handler(content_types=['animation'])
async def check_photo(message: types.Message):
    print(message)

# Принимает стикеры
@dp.message_handler(content_types=['video_note'])
async def check_sticker(message: types.Message):
    print(message)


# Принимает фото
@dp.message_handler(content_types=['sticker'])
async def check_photo(message: types.Message):
    print(message)


# СТАРТ
@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    
    user_id = message.chat.id
    username = message.chat.username
    
    bt_write = types.InlineKeyboardButton(
        text='🧨   Тапнуть   🧨',
        callback_data='choose_subject'
        )
    
    bt_line = [bt_write]
    keyboard = types.InlineKeyboardMarkup(resize_keyboard=True)
    
    keyboard.add(*bt_line)
    r_keyboard = await permission_markup(user_id)
    # Проверяем существует ли клиент в БД
    try:
        clients = Client.objects.filter(tg_id=user_id)
        if not clients:
            5/0
        try:
            if message.text == "/start":
                5/0
            await bot.delete_message(chat_id=user_id, message_id=message.message_id)
        except:
            print('нечего удалять')
        mes = await message.answer(
            '👀',
            reply_markup=r_keyboard
            )
        mes_id = mes.message_id
        await srd_message('save', mes_id, user_id)
        time.sleep(1)
        mes = await message.answer(
            f' - _Есть новая шутка ?_',
            reply_markup=keyboard,
            parse_mode="Markdown"
            )
        mes_id = mes.message_id
        await srd_message('save', mes_id, user_id)
    
    except:
        Client.objects.create(tg_id=user_id, tg_username=username)
        #await message.answer_video_note('DQACAgIAAxkBAANQZliZ2fxHZgx3htUr6-mosHfIZ4gAAqRJAALeKMFKW__2OdhzrNo1BA')

        # Дописать приветственный текст
        mes = await message.answer(
            '👀',
            reply_markup=r_keyboard
            )
        mes_id = mes.message_id
        await srd_message('save', mes_id, user_id)
        time.sleep(1)
        # Эхо сообщение
        message_text = ' я 🤖 БОТ "Шутка народа" v.0.1.'
        mes_id = await echo_message_fast(message_text, message.chat.id)
        await srd_message('save', mes_id, user_id)
        #
        mes = await message.answer(
            f' - _Есть новая шутка ?_',
            reply_markup=keyboard,
            parse_mode="Markdown"
            )
        mes_id = mes.message_id
        await srd_message('save', mes_id, user_id)
        
        # Сообщаем админу о новом пользователе
        await bot.send_message(
            chat_id=6382427107,
            text=f'Новый пользователь: @{username}'
            )


@dp.callback_query_handler(lambda c: c.data=='choose_subject')
async def choose_subject(call: types.CallbackQuery):

    # Клавиатура с темами
    subject_list = Subject.objects.filter()

    keyboard = types.InlineKeyboardMarkup()
    for subject in subject_list:
        subject_text = subject.text
        subject_callback = subject.callback
        bt_subject = types.InlineKeyboardButton(
            text=f'{subject_text}',
            callback_data=f'{subject_callback}'
        )
        keyboard.add(bt_subject)
        
    chat_id = call['from'].id
    
    #user_id = chat_id
    #await srd_message(command='del', user_id=user_id)

    message_list = DICT_MES[chat_id]
    mes_id = message_list[-1]
    await bot.edit_message_text(
        chat_id=chat_id,
        message_id=mes_id,
        text='🤖 *Выбери тему:*\n _- если темы нет в списке, выбирай "Другое"\n Определим и добавим ее)_',
        parse_mode="Markdown",
        reply_markup=keyboard
        )
    #mes_id = mes.message_id
    #await srd_message('save', mes_id, chat_id)


@dp.callback_query_handler(lambda c: c.data=='Its_all_Americas_fault' or c.data=='Children' or c.data=='Other' or c.data=='Men_and_women')
async def callback_write(call: types.CallbackQuery, state: FSMContext):
    
    chat_id = call['from'].id
    
    user_id = chat_id
    await srd_message(command='del', user_id=user_id)
    
    bt_cancel = types.KeyboardButton('❌ Отмена')
    r_keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    r_keyboard.add(bt_cancel)
    
    mes = await call.message.answer(
        '.',
        reply_markup=r_keyboard
    )
    mes_id = mes.message_id
    await srd_message('save', mes_id, chat_id)
    
    
    mes_id = await show_counter(chat_id)
    await srd_message('save', mes_id, chat_id)
    #await show_gomen(chat_id)
    
    message_text = '...тапай шутку в поле ввода сообщений...'
    mes_id = await echo_message_fast(message_text, chat_id)
    await srd_message('save', mes_id, chat_id)
    
    await state.set_state(WriteJoke.write.state)


# Обрабатывает написание шутки
@dp.message_handler(state=WriteJoke.write)
async def tap_joke(message: types.Message, state: FSMContext):
    user_id = message.chat.id
    
    chat_id = user_id
    
    await srd_message(command='del', user_id=user_id)
    
    if message.text == '❌ Отмена':
        await start(message)
        await state.finish()
        return
    
    # Сразу удаляем сообщение с отправленой шуткой
    await bot.delete_message(chat_id=chat_id, message_id=message.message_id)
    
    # Записываем шутку в базу
    username = message.chat.username
    users = Client.objects.filter(tg_id=user_id)
    users.reverse()
    user = users[0]
    if not user.joke:
        user.joke = message.text
        user.save()
    else:
        Client.objects.create(tg_id=user_id, tg_username=username, joke=message.text)
        
    
    bt_edit = types.InlineKeyboardButton(
        text='✍️ Редактировать',
        callback_data='choose_subject'
    )
    bt_ready = types.InlineKeyboardButton(
        text='👌 Готово',
        callback_data='ready'
    )

    bt_line = [bt_edit, bt_ready]

    keyboard = types.InlineKeyboardMarkup(resize_keyboard=True)
    keyboard.add(*bt_line)
    
    message_text = f'"{message.text}"'
    mes_id = await echo_message_fast(message_text, message.chat.id)
    await srd_message('save', mes_id, user_id)
    
    mes = await message.answer(
        text=f'🤖  - Хочешь исправить?',
        reply_markup=keyboard,
    )
    mes_id = mes.message_id
    await srd_message('save', mes_id, user_id)

    await state.finish()


@dp.callback_query_handler(lambda c: c.data=='ready')
async def ready(call: types.CallbackQuery):
    chat_id = call['from'].id

    user_id = chat_id
    await srd_message(command='del', user_id=user_id)

    users = Client.objects.filter(tg_id=chat_id)
    user = users[len(users) - 1]
    username = user.tg_username
    joke = user.joke
    
    await call.answer('Шутка добавлена!', show_alert=True)
    
    
    r_keyboard = await permission_markup(chat_id)
    
    mes = await call.message.answer(
        text='🤖 Я записал твою шутку.',
        reply_markup=r_keyboard
    )
    mes_id = mes.message_id
    await srd_message('save', mes_id, chat_id)
    

    message_text = ' - Все шутки будут озвучены на StandUP.\n  - Когда твоя шутка будет озвучена на StandUP(е), ты получишь свой бонус.\n  - Ты можешь подписаться на анонсы предстоящего StandUP(a).'
    mes_id = await echo_message_fast(message_text, chat_id)
    await srd_message('save', mes_id, chat_id)
    
    await bot.send_message(
        chat_id=6382427107,
        text=f'@{username}\n {joke}'
        )


@dp.callback_query_handler(lambda c: c.data=='restart')
async def call_start(call: types.CallbackQuery):
    user_id = call['from'].id
    await srd_message(command='del', user_id=user_id)
    await start(call.message)


@dp.callback_query_handler(lambda c: c.data=='follow_yes')
async def call_follow_yes(call: types.CallbackQuery):
    user_id = call['from'].id
    await srd_message(command='del', user_id=user_id)
    await follow_yes(call.message)


async def follow_no(message: types.Message):
    user_id = message.chat.id
    chat_id = user_id
    
    follow = Follow.objects.get(
            id=user_id
        )
    follow.delete()
    
    keyboard = await follow_inlinemarkup(chat_id)
    mes = await message.answer(
        text=f'Вы отписались от канала @StendUPPeoplebot!',
        reply_markup=keyboard
        )
    mes_id = mes.message_id
    await srd_message('save', mes_id, chat_id)


async def follow_yes(message: types.Message):
    user_id = message.chat.id
    chat_id = user_id
    
    Follow.objects.create(
            id=user_id,
            follow=True
        )
    
    keyboard = await follow_inlinemarkup(chat_id)
    mes = await message.answer(
        text=f'Вы подписались на канал @StendUPPeoplebot!',
        reply_markup=keyboard
        )
    mes_id = mes.message_id
    await srd_message('save', mes_id, chat_id)


@dp.message_handler()
async def dispatcher_message(message: types.Message):
    user_id = message.chat.id
    chat_id = user_id
    
    await bot.delete_message(chat_id=user_id, message_id=message.message_id)
    await srd_message(command='del', user_id=user_id)
    
    
    if message.text == '✅ Подписаться':
        await follow_yes(message)
        
    if message.text == 'Тихая 🤫 подписка':
        Follow.objects.create(
            id=user_id
        )
        keyboard = await follow_inlinemarkup(chat_id)
        mes = await message.answer(
            text=f'Вы подписались на канал @StendUPPeoplebot!\nТихая 🤫 подписка, без явных уведомлений.',
            reply_markup=keyboard
            )
        mes_id = mes.message_id
        await srd_message('save', mes_id, chat_id)

    if message.text == '❌ Отписаться':
        await follow_no(message)
    
    if message.text == '♻️ restart ♻️':
        await start(message)
        
    if message.text == 'ℹ️ О проекте':
        keyboard = await follow_inlinemarkup(user_id)
        mes = await message.answer(
            text=f'🤖\n-Проект: *Шутка народа*\n\n 1. ✍️ Записываем шутку\n\n 2. Получаем уведомление о предстоящем событии 📬\n\n 3. Ждем свою шутку 🫠\n\n 4. Получаем донат 🤑 от нашего канала.\n',
            reply_markup=keyboard,
            parse_mode="Markdown"
            )
        mes_id = mes.message_id
        await srd_message('save', mes_id, chat_id)


async def show_counter(chat_id):
    objs =  '4️⃣ 3️⃣ 2️⃣ 1️⃣ 0️⃣ 🎤'
    entries = objs.split()

    text = '....................................5️⃣....................................'
    msg = await bot.send_message(chat_id, text=text)

    for tbp in entries:
        time.sleep(0.2)
        text = f'....................................{tbp}....................................'
        await bot.edit_message_text(
            chat_id=chat_id,
            message_id=msg.message_id,
            text=text
            )
    
    return msg.message_id



async def show_gomen(chat_id):
    objs =  '🚶‍♂️ 🚶‍♂️ 🚶‍♂️ 🚶‍♂️ 🚶‍♂️ 🚶‍♂️ 🚶‍♂️ 🚶‍♂️ 🚶‍♂️ 🚶‍♂️ 🚶‍♂️ 🚶‍♂️ 🚶‍♂️ 🚶‍♂️ 🚶‍♂️ 🚶‍♂️ 🚶‍♂️ 🚶‍♂️ 🚶‍♂️ 🚶‍♂️'
    entries = objs.split()
    count = len(entries)
    print(count)
    text='.loading                🎤'
    for _ in range(count):
        text = text + '.'
    print(text)
    msg = await bot.send_message(chat_id, text=text)

    count_minus = count*2 - 1

    for tbp in entries:
        time.sleep(0.1)
        text = text[:count_minus]
        tbp = tbp + '..' + tbp + '..'
        text = text+tbp
        count_minus = count_minus - 2
        await bot.edit_message_text(
            chat_id=chat_id,
            message_id=msg.message_id,
            text=text
            )

        if count_minus <= 22:
            await bot.delete_message(chat_id=chat_id, message_id=msg.message_id)
            break


# Медленный вывод сообщений
async def echo_message_fast(message_text, chat_id):
    keyboard = None
    if message_text == '🤖\n - Все шутки будут озвучены на StandUP.\n\n - Когда твоя шутка будет озвучена на StandUP(е), ты получишь свой бонус.\n\n - Ты можешь подписаться на анонсы предстоящего StandUP(a).':
        bt_write = types.InlineKeyboardButton(
            text='Написать еще',
            callback_data='choose_subject'
            )
        bt_line = [bt_write]
        keyboard = types.InlineKeyboardMarkup(resize_keyboard=True)
        keyboard.add(*bt_line)
    
    entries = message_text.split()
    msg = await bot.send_message(chat_id, text='_', reply_markup=keyboard)
    
    tbp = message_text[:1]
    for x in entries:
        x = f'{x} '
        tbp = tbp + x
        await bot.edit_message_text(
            chat_id=chat_id,
            message_id=msg.message_id,
            text=f'_{tbp}_',
            parse_mode="Markdown",
            reply_markup=keyboard
            )
    return msg.message_id


# Перехватывает сообщения inline режима(доработать)
@dp.inline_handler()
async def inline_handler(inline_query: types.InlineQuery):
    text = inline_query.query or 'Шутка_народа'
    link = 'https://ru.wikipedia.org/wiki/'+text
    input_content = types.InputTextMessageContent(link)
    result_id: str = hashlib.md5(text.encode()).hexdigest()
    
    item = types.InlineQueryResultArticle(
        input_message_content=input_content,
        id=result_id,
        url=link,
        title='Поиск в wikipedia',
    )
    
    await bot.answer_inline_query(
        inline_query_id=inline_query.id,
        results=[item],
        cache_time=1
    )


executor.start_polling(dp)