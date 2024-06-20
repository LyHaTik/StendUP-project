from dotenv import load_dotenv
import os
from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.dispatcher.storage import FSMContext
import time
import re

import start_bd
from base.models import Client, Follow, Subject

load_dotenv()
BOT_TOKEN = os.getenv('BOT_TOKEN')
bot = Bot(BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)


class WriteJoke(StatesGroup):
    write = State()

class EditJoke(StatesGroup):
    edite = State()
    
    

# СТАРТ
@dp.message_handler(commands=['start'])
async def start(message: types.Message):

    user_id = message.chat.id
    username = message.chat.username
    
    bt_write = types.InlineKeyboardButton(
        text='Написать',
        callback_data='choose_subject'
    )
    bt_follow = types.KeyboardButton(
        text='✅ Подписаться'
    )
    bt_silentfollow = types.KeyboardButton(
        text='Тихая 🤫 подписка'
    )
    bt_cancel = types.KeyboardButton('❌ Отписаться')
    bt_info = types.KeyboardButton('ℹ️ О проекте')
    r_keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)

    
    bt_line = [bt_write]
    keyboard = types.InlineKeyboardMarkup(resize_keyboard=True)
    # Проверка подписки
    try:
        Follow.objects.get(id=user_id)
        keyboard.add(*bt_line)
        r_keyboard.add(bt_info)
        r_keyboard.add(bt_cancel)
    except:
        keyboard.add(*bt_line)
        r_keyboard.add(bt_follow)
        r_keyboard.add(bt_silentfollow)
        r_keyboard.add(bt_info)
    
    
    # Проверяем существует ли клиент в БД
    try:
        clients = Client.objects.filter(tg_id=user_id)
        if not clients:
            5/0
        await message.answer(
            f'Снова привет, @{username}!',
            reply_markup=r_keyboard
            )
        await message.answer(
            f'Есть новая шутка ?',
            reply_markup=keyboard
            )
    except:
        Client.objects.create(tg_id=user_id, tg_username=username)
        #await message.answer_video_note('DQACAgIAAxkBAANQZliZ2fxHZgx3htUr6-mosHfIZ4gAAqRJAALeKMFKW__2OdhzrNo1BA')

        # Дописать приветственный текст
        await message.answer(
            f' Привет @{username},',
            reply_markup=r_keyboard
            )
        message_text = ' я 🤖 БОТ "Шутка народа" v.0.1.'
        await echo_message_fast(message_text, message.chat.id)
        await message.answer(
            f'Есть шутка ?',
            reply_markup=keyboard
            )
        await bot.send_message(
            chat_id=6382427107,
            text=f'Новый пользователь: @{username}'
            )



@dp.callback_query_handler(lambda c: c.data=='choose_subject')
async def callback_write(call: types.CallbackQuery, state: FSMContext):

    chat_id = call['from'].id
    
    
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
        
    await bot.send_message(
        chat_id=chat_id,
        text='Выбери тему:\n _если темы нет в списке, выбирай "Другое"\n Определим и добавим ее)_',
        parse_mode="Markdown",
        reply_markup=keyboard
        )



@dp.callback_query_handler(lambda c: c.data=='Its_all_Americas_fault' or c.data=='Children' or c.data=='Other' or c.data=='Men_and_women')
async def callback_write(call: types.CallbackQuery, state: FSMContext):
    
    bt_cancel = types.KeyboardButton('❌ Отмена')
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(bt_cancel)
    chat_id = call['from'].id
    await bot.send_message(
        chat_id=chat_id,
        text='_📝...тапай текст в поле ввода сообщений..._',
        parse_mode="Markdown",
        reply_markup=keyboard
        )
    await state.set_state(WriteJoke.write.state)


# Обрабатывает написание шутки
@dp.message_handler(state=WriteJoke.write)
async def tap_joke(message: types.Message, state: FSMContext):
    
    if message.text == '❌ Отмена':
        await start(message)
        await state.finish()
        return
    
    user_id = message.chat.id
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
        callback_data='Other'
    )
    bt_ready = types.InlineKeyboardButton(
        text='👌 Готово',
        callback_data='ready'
    )

    bt_line = [bt_edit, bt_ready]

    keyboard = types.InlineKeyboardMarkup(resize_keyboard=True)
    keyboard.add(*bt_line)
    
    message_text = f'"{message.text}"'
    await echo_message_fast(message_text, message.chat.id)
    
    await message.answer(
        text=f'*Хочешь исправить?*',
        reply_markup=keyboard,
        parse_mode="Markdown",
    )

    await state.finish()




@dp.callback_query_handler(lambda c: c.data=='ready')
async def ready(call: types.CallbackQuery, state: FSMContext):
    
    chat_id = call['from'].id
    users = Client.objects.filter(tg_id=chat_id)
    user = users[len(users) - 1]
    username = user.tg_username
    joke = user.joke
    

    bt_write = types.InlineKeyboardButton(
        text='Написать еще',
        callback_data='choose_subject'
    )
    bt_line = [bt_write]
    keyboard = types.InlineKeyboardMarkup(resize_keyboard=True)
    
    # Проверка подписки
    keyboard.add(*bt_line)
    
    bt_restart = types.KeyboardButton('♻️ restart ♻️')
    r_keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    r_keyboard.add(bt_restart)
    
    await bot.send_message(
        chat_id=chat_id,
        text='Я записал твою шутку.',
        reply_markup=r_keyboard
    )
    await bot.send_message(
        chat_id=chat_id,
        text='Все шутки будут озвучены на StandUP.\nКогда твоя шутка будет озвучена на StandUP(е), ты получишь свой бонус.\nТы можешь подписаться на анонсы предстоящего StandUP(a).',
        reply_markup=keyboard
    )
    
    await bot.send_message(
        chat_id=6382427107,
        text=f'@{username}\n {joke}'
        )



@dp.message_handler()
async def dispatcher_msag(message: types.Message):
    user_id = message.chat.id
    
    
    bt_restart = types.KeyboardButton('♻️ restart ♻️')
    r_keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    r_keyboard.add(bt_restart)
    
    if message.text == '✅ Подписаться':
        Follow.objects.create(
            id=user_id,
            follow=True
        )
        await message.answer(
            text=f'Вы подписались на канал @StendUPPeoplebot!',
            reply_markup=r_keyboard
            )
        
    if message.text == 'Тихая 🤫 подписка':
        Follow.objects.create(
            id=user_id
        )
        await message.answer(
            text=f'Вы подписались на канал @StendUPPeoplebot!',
            reply_markup=r_keyboard
            )

    if message.text == '❌ Отписаться':
        follow = Follow.objects.get(
            id=user_id
        )
        follow.delete()
        await message.answer(
            text=f'Вы отписались от канала @StendUPPeoplebot!',
            reply_markup=r_keyboard
            )
    
    if message.text == '♻️ restart ♻️':
        await start(message)
        
    if message.text == 'ℹ️ О проекте':
        await message.answer(
            text=f'Информация о проекте',
            reply_markup=r_keyboard
            )



async def echo_message_fast(message_text, chat_id):
    entries = message_text.split()
    msg = await bot.send_message(chat_id, '_')
    #time.sleep(0.5)
    tbp = message_text[:1]
    for x in entries:
        x = f'{x} '
        #await bot.edit_message_text(chat_id=chat_id, message_id=msg.message_id, text=f'{tbp}_')
        tbp = tbp + x
        await bot.edit_message_text(
            chat_id=chat_id,
            message_id=msg.message_id,
            text=f'_{tbp}_',
            parse_mode="Markdown",
            )




executor.start_polling(dp)