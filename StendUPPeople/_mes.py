from aiogram import Bot
from dotenv import load_dotenv
import os


load_dotenv()
BOT_TOKEN = os.getenv('BOT_TOKEN')
bot = Bot(BOT_TOKEN)


global DICT_MES
DICT_MES = {}

async def srd_message(command, mes_id=None, user_id=None):
    if command == 'save':
        if user_id in DICT_MES.keys():
            mes_id_list = DICT_MES[user_id]
            mes_id_list.append(mes_id)
            DICT_MES[user_id] = mes_id_list
            print(DICT_MES)
            return
        DICT_MES[user_id] = [mes_id]
    
    if command == 'del':
        try:
            mes_list = DICT_MES[user_id]
            for mes_id in mes_list: 
                await bot.delete_message(chat_id=user_id, message_id=mes_id)

            DICT_MES[user_id] = []
        except:
            DICT_MES[user_id] = []
    print(DICT_MES)