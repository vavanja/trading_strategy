import asyncio
import os

import telebot.types
from telebot.async_telebot import AsyncTeleBot
from dotenv import load_dotenv
from main import main


load_dotenv('.env')
token = os.getenv('BOT_TOKEN')

bot = AsyncTeleBot(token)
key = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
keyboard = telebot.types.KeyboardButton(text='/test')
key.add(keyboard)


@bot.message_handler(commands=['test'])
async def start_strategy(message):
    await bot.send_message(message.chat.id, text='~~~~~~ Starting strategy ~~~~~')
    await main((bot, message))


@bot.message_handler(commands=['start'])
async def start(message):
    await bot.send_message(message.chat.id, text="Hello it is trading bot, let's test my trade strategy :)",
                           reply_markup=key)

asyncio.run(bot.polling())
