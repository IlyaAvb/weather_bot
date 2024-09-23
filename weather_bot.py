import json
from email.policy import default

import telebot
from telebot import types
import requests
import fake_useragent
from googletrans import Translator
import sqlite3

from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton

API_key = '3865070e623c4324b55122415242309'


bot = telebot.TeleBot('')

translator = Translator()

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, message.from_user.username)
    if message.from_user.username == 'avarde808':
        markup = ReplyKeyboardMarkup(resize_keyboard=True)
        btn = KeyboardButton('Все пользователи')
        markup.add(btn)
    else:
        markup = ''

    bot.send_message(message.chat.id, 'Привет! \n\n Напиши название города,'
                                      ' чтобы узнать погоду \n\n'
                                      '☀️🌤⛅️⛈🌦🌥🌧', reply_markup=markup)


    conn = sqlite3.connect('get_weatger_bot.db')
    cur = conn.cursor()

    cur.execute('CREATE TABLE IF NOT EXISTS requests (id INTEGER PRIMARY KEY AUTOINCREMENT, user TEXT, description TEXT)')

    conn.commit()
    conn.close()


@bot.message_handler(func=lambda message: True)
def handle_message(message):

    if message.text == 'Все пользователи':
        conn = sqlite3.connect('get_weatger_bot.db')
        cur = conn.cursor()

        cur.execute('SELECT * FROM requests')
        rows = cur.fetchall()
        conn.close()

        if rows:
            response = 'Пользователи и запросы \n\n'
            for row in rows:
                response += f'ID: {row[0]} username: {row[1]} \n'
            bot.send_message(message.chat.id, response)

        else:
            bot.send_message(message.chat.id, 'Нет записей о пользователях')
    else:
        get_weather(message)

def get_weather(message):

    city = message.text.strip().lower()
    bot.send_message(message.chat.id, 'Одну минуту...')
    try:
        response = requests.get(f'https://api.weatherapi.com/v1/current.json?key={API_key}&q={city}')
        data = response.json()
        name_city = data['location']['name']
        temp_c = data['current']['temp_c']
        description_text = data['current']['condition']['text']
        description_text_RU = translator.translate(description_text, dest='ru').text
        feelslike_c = data['current']['feelslike_c']
        bot.reply_to(message, f"Сейчас погода в городе «{name_city}»: \n")
        caption = (f"Температура - {temp_c} градусов \n"
                   f"Описание - {description_text_RU} \n"
                   f"Ощущается как - {feelslike_c} градусов \n")
        open_file = ''
        if temp_c < 20:
            open_file = 'rain.jpg'
        elif temp_c > 20:
            open_file = 'sunny.jpg'
        else:
            open_file = ''
        file = open(open_file, 'rb')
        bot.send_photo(message.chat.id, file, caption=caption)
        username = message.from_user.username
        commit_to_db(username=username, caption=caption)
    except Exception:
        bot.reply_to(message, 'Что-то пошло не так...😔')

def commit_to_db(username, caption):
    conn = sqlite3.connect('get_weatger_bot.db')
    cur = conn.cursor()

    cur.execute('INSERT INTO requests (user, description) VALUES (?, ?)', (username, caption))

    conn.commit()
    conn.close()


# bot.infinity_polling()

