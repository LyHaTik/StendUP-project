from aiogram import Bot, Dispatcher, executor, types
from base.models import Client, Follow, Subject


async def permission_markup(user_id):
    
    bt_restart = types.KeyboardButton('♻️ restart ♻️')
    
    bt_follow = types.KeyboardButton(
        text='✅ Подписаться'
    )
    bt_silentfollow = types.KeyboardButton(
        text='Тихая 🤫 подписка'
    )
    bt_cancel = types.KeyboardButton('❌ Отписаться')
    bt_info = types.KeyboardButton('ℹ️ О проекте')
    r_keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
    
    # Проверка подписки
    follow = await check_follow(user_id)
    if follow:
        r_keyboard.add(bt_restart)
        r_keyboard.add(bt_info)
        r_keyboard.add(bt_cancel)
    else:
        r_keyboard.add(bt_restart)
        r_keyboard.add(bt_follow)
        r_keyboard.add(bt_silentfollow)
        r_keyboard.add(bt_info)
    return r_keyboard


# Inline подписка
async def follow_inlinemarkup(user_id):
    
    bt_rest = types.InlineKeyboardButton(
            text='♻️ restart ♻️',
            callback_data='restart'
            )
    bt_follow_yes = types.InlineKeyboardButton(
            text='✅ Подписаться',
            callback_data='follow_yes'
            )

    keyboard = types.InlineKeyboardMarkup(resize_keyboard=True)
    
    follow = await check_follow(user_id)
    if not follow:
        bt_line1 = [bt_follow_yes]
        keyboard.add(*bt_line1)
        bt_line2 = [bt_rest]
    else:
        bt_line2 = [bt_rest]
    keyboard.add(*bt_line2)
    
    return keyboard


# Проверяет подписку
async def check_follow(user_id):
    try:
        Follow.objects.get(id=user_id)
        check = True
    except:
        check = False
    return check