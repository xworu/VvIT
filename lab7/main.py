import telebot
from telebot import types

import psycopg2
import requests

token = "6222613681:AAFXOQNY_Zx9exTCSYLNhsCzXtPjlYgAwbg"
bot = telebot.TeleBot(token)
conn = psycopg2.connect(database="bot_db",
                        user="postgres",
                        password=" ",
                        host="localhost",
                        port="5432")

cursor = conn.cursor()

res = requests.get("http://worldtimeapi.org/api/timezone/Europe/Moscow")
data = res.json()
current_week = data["week_number"] % 2
if current_week == 0:
    next_week = 1
else:
    next_week = 0

cursor.execute('UPDATE bot.current_week SET current_week = ' + ("1" if data["week_number"] % 2 else "0") +
               ' WHERE current_week <> ' + ("1" if data["week_number"] % 2 else "0"))
conn.commit()

MONDAY, TUESDAY, WEDNESDAY = "Понедельник", "Вторник", "Среда"
THURSDAY, FRIDAY = "Четверг", "Пятница"
CURRENT_WEEK, NEXT_WEEK = "Расписание на текущую неделю", "Расписание на следующую неделю"

WEEKDAY = {
    MONDAY: 1, TUESDAY: 2, WEDNESDAY: 3,
    THURSDAY: 4, FRIDAY: 5}


@bot.message_handler(commands=['start'])
def start(message):
    keyboard = types.ReplyKeyboardMarkup()
    keyboard.row("/help")
    bot.send_message(message.chat.id, 'Нажмите /help, чтобы узнать, что я могу', reply_markup=keyboard)


@bot.message_handler(commands=['help'])
def start_message(message):
    bot.send_message(message.chat.id,
                     'Я умею показывать расписание и информацию о текущей неделе,'
                     ' а также предоставить ссылку на официальный сайт МТУСИ.\n\n'
                     '/help — показать список доступных команд\n'
                     '/mtuci — получить ссылку на официальный сайт МТУСИ\n'
                     '/week - получить информацию о том, является четной ли или нет текущая неделя\n'
                     '/timetable - получить расписание \n'
                     )


@bot.message_handler(commands=['mtuci'])
def mtuci_command(message):
    bot.send_message(message.chat.id, 'Официальный сайт МТУСИ - https://mtuci.ru/')


@bot.message_handler(commands=['week'])
def week_command(message):
    bot.send_message(
        message.chat.id,
        "Сейчас идет" + (" нечетная (верхняя) " if current_week == 1 else " четная (нижняя) ") + "неделя."
    )


@bot.message_handler(commands=['timetable'])
def timetable_command(message):
    keyboard = types.ReplyKeyboardMarkup()
    keyboard.row(MONDAY, TUESDAY, WEDNESDAY)
    keyboard.row(THURSDAY, FRIDAY)
    keyboard.row(CURRENT_WEEK, NEXT_WEEK)
    bot.send_message(
        message.chat.id,
        'Выберите день, для которого показать расписание', reply_markup=keyboard)


def day_timetable(text):
    day = WEEKDAY[text]
    cursor.execute('SELECT * FROM bot.timetable '
                   'JOIN bot.subject ON timetable.subject = bot.subject.id '
                   'JOIN bot.teacher ON timetable.teacher = bot.teacher.id '
                   'WHERE week = ' + "(SELECT current_week FROM bot.current_week)" + ' AND day = ' + str(day))
    timetable = list(cursor.fetchall())
    result = text
    for i in timetable:
        result += '\n ' + i[5] + '\n ' + i[8] + ('\n ' if i[10] != ' ' else ' ') + i[10] + (
            '\n ' if i[4] != ' ' else ' ') + i[4] + ('\n ' if i[4] != ' ' else ' ')
    return result


def week_timetable(text):
    cursor.execute('SELECT * FROM bot.timetable '
                   'JOIN bot.subject ON timetable.subject = bot.subject.id '
                   'JOIN bot.teacher ON timetable.teacher = bot.teacher.id '
                   'WHERE week = ' + (str(next_week) if text else "(SELECT current_week FROM bot.current_week)") +
                   ' ORDER BY day')
    timetable = list(cursor.fetchall())
    result = 'Понедельник'
    for i in timetable[0:5]:
        result += '\n ' + i[5] + '\n ' + i[8] + ('\n ' if i[10] != ' ' else ' ') + i[10] + (
            '\n ' if i[4] != ' ' else ' ') + i[4] + '\n'

    result += '\n __________\n '
    result += '\nВторник'
    for i in timetable[5:10]:
        result += '\n ' + i[5] + '\n ' + i[8] + ('\n ' if i[10] != ' ' else ' ') + i[10] + (
            '\n ' if i[4] != ' ' else ' ') + i[4] + '\n'

    result += '\n __________\n '
    result += '\nСреда'
    for i in timetable[10:15]:
        result += '\n ' + i[5] + '\n ' + i[8] + ('\n ' if i[10] != ' ' else ' ') + i[10] + (
            '\n ' if i[4] != ' ' else ' ') + i[4] + '\n'

    result += '\n __________\n '
    result += '\nЧетверг'
    for i in timetable[15:20]:
        result += '\n ' + i[5] + '\n ' + i[8] + ('\n ' if i[10] != ' ' else ' ') + i[10] + (
            '\n ' if i[4] != ' ' else ' ') + i[4] + '\n'

    result += '\n __________\n '
    result += '\nПятница'
    for i in timetable[20:25]:
        result += '\n ' + i[5] + '\n ' + i[8] + ('\n ' if i[10] != ' ' else ' ') + i[10] + (
            '\n ' if i[4] != ' ' else ' ') + i[4] + '\n'

    return result


@bot.message_handler(content_types=["text"])
def answer(message):
    text = message.text

    if text in [MONDAY, TUESDAY, WEDNESDAY, THURSDAY, FRIDAY]:
        bot.send_message(message.chat.id, day_timetable(text))
    elif text in [CURRENT_WEEK, NEXT_WEEK]:
        bot.send_message(message.chat.id, week_timetable(text == NEXT_WEEK))
    else:
        bot.send_message(message.chat.id, "Извините, я Вас не понял")


bot.infinity_polling()
