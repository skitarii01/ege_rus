import logging
import shutil

import telebot
import markups as mups
import sqlite3 as sql
import random
import os
from telebot import types
import bases0
import requests
from bs4 import BeautifulSoup

# main variables
TOKEN = ''
with open('TOKEN.txt') as fl:
    for i in fl:
        TOKEN = i
        break
bot = telebot.TeleBot(TOKEN)

con = sql.connect('users.db')


def is_profile_exist(id):
    if os.path.exists("./users_data/%s" % (id)):
        return 1
    else:
        return 0


# проверяет был ли выбран вариант с клавиатуры или нет
def check_is_answer_correct(msg, arr):
    if msg.text in arr:
        return 1
    else:
        return 0


def profile_generation(id, name):
    user = (id, name)
    try:
        with sql.connect("users.db") as con:

            cur = con.cursor()
            cur.execute("CREATE TABLE IF NOT EXISTS users("
                        "userid INT PRIMARY KEY,"
                        "name TEXT);")
            cur.execute("SELECT * FROM USERS;")
            existing_users = cur.fetchall()

            for i in existing_users:
                if i[0] == id:
                    return 2

            cur.execute("CREATE TABLE IF NOT EXISTS users("
                        "userid INT PRIMARY KEY,"
                        "name TEXT);")
            cur.execute("INSERT INTO users VALUES(?, ?)", user)
            print('./users_data/%s' % (id))
            os.mkdir('./users_data/%s' % (id))

            con.commit()
        return 1
    except Exception:
        return 0


# добавляет в профиль готовую базу
def add_existing_base(msg):
    chat_id = msg.chat.id
    if os.path.exists("./users_data/%s/%s.db" % (msg.from_user.id, msg.text)):
        bot.send_message(
            chat_id, 'это у вас есть', reply_markup=mups.greetings)
        return
    try:
        print(msg.text)
        shutil.copy("./prepared_bases/%s.db" %
                    (msg.text), "./users_data/%s" % (msg.from_user.id))
        print("./prepared_bases/%s.db" %
              (msg.text), "./users_data/%s" % (msg.from_user.id))
        bot.send_message(chat_id, 'добавлено',
                         reply_markup=mups.greetings)
    except Exception:
        bot.send_message(
            chat_id, 'чтото пошло не по плану...', reply_markup=mups.greetings)


def get_paronim():
    url = 'https://paronymonline.ru/ege.html'
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'lxml')
    quotes = soup.find_all('ol', class_='list-ege')
    lol = quotes[0].find_all('li')
    return lol[random.randint(0, len(lol) - 1)].text


def choose_base(msg):
    chat_id = msg.chat.id
    user_id = msg.from_user.id
    arr = bases0.get_list_of_bases(user_id)

    if check_is_answer_correct(msg, arr):
        base = bases0.activate_base(msg, bot)
        msg = bot.send_message(
            chat_id, "Сколько слов для тренировки?", reply_markup=mups.nums)
        bot.register_next_step_handler(msg, base.generate_exercise)
    else:
        bot.send_message(chat_id, 'неверный выбор :(', reply_markup=mups.greetings)



@bot.message_handler(commands=['start', 'go'])
def start_handler(message):
    user_id = message.from_user.id
    chat_id = message.chat.id
    if not is_profile_exist(message.from_user.id):
        bot.send_message(chat_id, 'привет!', reply_markup=mups.source_markup)
    else:
        bot.send_message(chat_id, 'привет!',
                         reply_markup=mups.greetings)
    logging.info("user %d started working with me" % (user_id))


@bot.message_handler(content_types=['text'])
def text_handler(message):
    text = message.text.lower()
    chat_id = message.chat.id
    user_id = message.from_user.id

    if text == 'инициализация' and not is_profile_exist(user_id):
        success = profile_generation(
            user_id, message.from_user.username)
        if success == 1:
            bot.send_message(
                chat_id, 'Создание прошло успешно', reply_markup=mups.greetings)
            logging.info('profile creation for user %s succesful')
        elif success == 2:
            bot.send_message(
                chat_id, 'Профиль уже создан', reply_markup=mups.greetings)
        else:
            bot.send_message(
                chat_id, 'чтото пошло не по плану...', reply_markup=mups.greetings)
            logging.error('profile creation for user %s is not succesful')
        return
    if is_profile_exist(user_id):
        if text == 'добавить словари':
            msg = bot.send_message(chat_id, 'выбирайте',
                                   reply_markup=mups.prepared_bases)
            bot.register_next_step_handler(msg, add_existing_base)

        elif text == 'вернуться':
            bot.send_message(chat_id, 'хорошо', reply_markup=mups.greetings)

        elif text == 'потренироваться':
            msg = bot.send_message(chat_id, 'выбирайте', reply_markup=bases0.generate_personal_bases_clav(message))
            bot.register_next_step_handler(msg, choose_base)

        elif text == 'посмотреть пароним':
            msg = bot.send_message(chat_id, get_paronim(), reply_markup=mups.greetings)

while True:
    try:
        print('connecting')
        bot.polling()
    except Exception:
        print('smthg is wrong, reconnecting')
