from telebot import types

source_markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
source_markup_btn1 = types.KeyboardButton('инициализация')
source_markup.add(source_markup_btn1)

greetings = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
greetings_btn1 = types.KeyboardButton('Добавить словари')
greetings_btn2 = types.KeyboardButton('потренироваться')
greetings_btn3 = types.KeyboardButton('посмотреть пароним')
greetings.add(greetings_btn1, greetings_btn2, greetings_btn3)

training = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
training_btn1 = types.KeyboardButton('вернуться')
training.add(training_btn1)

nums = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
nums_btn1 = types.KeyboardButton('5')
nums_btn2 = types.KeyboardButton('10')
nums_btn3 = types.KeyboardButton('15')
nums_btn4 = types.KeyboardButton('20')
nums_btn5 = types.KeyboardButton('Вернуться')
nums.add(nums_btn1, nums_btn2, nums_btn3, nums_btn4, nums_btn5)

prepared_bases = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
prepared_bases_btn1 = types.KeyboardButton('ударения')
prepared_bases_btn4 = types.KeyboardButton('Вернуться')
prepared_bases.add(prepared_bases_btn1,
                   prepared_bases_btn4)
