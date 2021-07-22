# библиотека классов словарей
from telebot import types
import os
import shutil
import sqlite3 as sql
import random
import markups as mups



def get_list_of_bases(user_id):
    files = os.listdir('./users_data/%s' % (user_id))
    print(files)
    for i in range(len(files)):
        files[i] = files[i].split('.')[0]
    return files


def generate_personal_bases_clav(msg):
    mup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    b = []
    arr = get_list_of_bases(msg.from_user.id)
    for i in arr:
        b.append(types.KeyboardButton(i))
    for i in b:
        mup.add(i)
    last = types.KeyboardButton('вернуться')
    mup.add(last)
    return mup


class base(object):

    def __init__(self, base_name, bot, user_id):
        """Constructor"""
        self.user_id = user_id
        self.base_name = base_name
        self.bot = bot
        self.number_of_answers = 0
        self.counter = 0
        self.arr_wrong = []
        self.key = -1

    # функция для получения статистики профиля
    def get_statistic(self):
        data = []
        with sql.connect("./users_data/%s/%s.db" % (self.user_id, self.base_name)) as con:
            cur = con.cursor()
            cur.execute("CREATE TABLE IF NOT EXISTS base0("
                        "attempt TEXT,"
                        "answer TEXT,"
                        "right_number INT,"
                        "all_number INT);")
            cur.execute("SELECT * FROM base0;")
            data = cur.fetchall()

            con.commit()
        data = sorted(data, key=lambda x: x[2])
        data = data[::-1]
        s = "5 лучших\n"
        for i in range(5):
            s += data[i][1] + "(%d / %d)" % (data[i][2], data[i][3]) + "\n"
        return s

    # получить все данные с sql словаря
    def get_content(self):
        with sql.connect("./users_data/%s/%s.db" % (self.user_id, self.base_name)) as con:
            cur = con.cursor()
            cur.execute("CREATE TABLE IF NOT EXISTS base0("
                        "attempt TEXT,"
                        "answer TEXT,"
                        "right_number INT,"
                        "all_number INT);")
            cur.execute("SELECT * FROM base0;")
            data = cur.fetchall()

            data2 = []
            for i in data:
                number = round(1000 * ((i[3] - i[2]) / i[3]))
                for j in range(number):
                    data2.append(i)
            con.commit()
        return data2

    # генерация клавы вариантов ответа
    def clav_generation(self, arr):
        mup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
        b = []
        for i in arr:
            b.append(types.KeyboardButton(i))
        for i in b:
            mup.add(i)
        last = types.KeyboardButton('вернуться')
        mup.add(last)
        return mup

    # без приоритетов
    def get_random_word_from_base(self):
        data2 = self.get_content()
        self.key = random.randint(0, len(data2) - 1)
        return data2[self.key][0]

    def generate_variants_func(self, obj):
        return obj

        # первый вызов функции next_exercise( генерация счетчика для количества выполненных упражнений)

    def generate_exercise(self, msg):
        try:
            self.arr_wrong = []
            self.number_of_answers = int(msg.text)
            self.counter = 0

            # вывод рандомного слова
            s = self.get_random_word_from_base()
            arr = self.generate_variants_func(s)
            mp = self.clav_generation(arr)
            msg = self.bot.send_message(msg.chat.id, s, reply_markup=mp)
            self.bot.register_next_step_handler(msg, self.next_exercise)
        except Exception:
            msg = self.bot.send_message(msg.chat.id, 'неверный формат', reply_markup=mups.greetings)

    # один вызов функции - обработка одного упражнения
    def next_exercise(self, msg):
        self.counter += 1
        word = msg.text
        if word == 'вернуться':
            self.bot.send_message(msg.chat.id, 'хорошо',
                                  reply_markup=mups.greetings)
            return
        is_right = False
        data2 = self.get_content()
        with sql.connect("./users_data/%s/%s.db" % (self.user_id, self.base_name)) as con:

            cur = con.cursor()
            cur.execute("CREATE TABLE IF NOT EXISTS base0("
                        "attempt TEXT,"
                        "answer TEXT,"
                        "right_number INT,"
                        "all_number INT);")

            answer = data2[self.key][1]

            # обновляем статы
            if answer == word:
                is_right = True
                cur.execute("UPDATE base0 SET right_number = ? WHERE attempt = ?",
                            (data2[self.key][2] + 1, data2[self.key][0]))
                cur.execute("UPDATE base0 SET all_number = ? WHERE attempt = ?",
                            (data2[self.key][3] + 1, data2[self.key][0]))
            else:
                cur.execute("UPDATE base0 SET all_number = ? WHERE attempt = ?",
                            (data2[self.key][3] + 1, data2[self.key][0]))
            con.commit()
        if not is_right:
            self.arr_wrong.append([data2[self.key][0], data2[self.key][1]])

        if self.counter == self.number_of_answers:
            s = "Результат: %d / %d" % (self.number_of_answers -
                                        len(self.arr_wrong), self.number_of_answers)
            s += "\n\nОшибки:\n"
            for i in self.arr_wrong:
                s += i[0] + " - " + i[1] + '\n'
            self.bot.send_message(msg.chat.id, s, reply_markup=mups.training)

        else:
            s = self.get_random_word_from_base()

            arr = self.generate_variants_func(s)
            mp = self.clav_generation(arr)
            msg = self.bot.send_message(msg.chat.id, s, reply_markup=mp)
            self.bot.register_next_step_handler(msg, self.next_exercise)

    # проверяет формат данных на добавление в библиотеку
    def check_format(self, data):
        return 1

class rus_4(base):
    glasnie = 'уеыаоэяиюё'

    # ударения егэ
    def generate_variants_func(self, word):
        word = word.lower()
        arr = []

        for i in range(len(word)):
            if word[i] in self.glasnie:
                arr.append(word[:i] + word[i].upper() + word[i + 1:])
        return arr

    # проверяет формат данных на добавление в библиотеку
    def check_format(self, data):
        if len(data.split()) > 1 or len(data) <= 3:
            return False
        n = 0
        for i in data:
            if i == i.upper() and i.lower() in self.glasnie:
                n += 1
            elif i == i.upper():
                return False
        if n != 1:
            return False


def activate_base(msg, bot):
    base_name = msg.text
    base = ""
    if base_name == 'ударения':
        base = rus_4('ударения', bot, msg.from_user.id)

    return base
