import telebot
from telebot import types
import os
import logging
import time

from dotenv import load_dotenv
from db import BotDB


BotDB = BotDB()
load_dotenv()
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
bot = telebot.TeleBot(TELEGRAM_TOKEN)


count = 0
answer = 0


@bot.message_handler(commands=['start', 'Отмена'])
def wake_up(message):
    """Главное меню."""
    global count
    global answer
    count = 0
    answer = 0
    BotDB.drop_null()
    data = BotDB.user_exist(message)
    if data:
        text = f'{message.chat.first_name} {message.chat.last_name}, выбери интресующий тебя пункт.'
        list_tasks = ['/Посмотреть_записи', '/Удалить_запись', '/Новая_запись']
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=False, resize_keyboard=True)
    else:
        text = f'Привет,{message.chat.first_name} {message.chat.last_name}! Выбери интресующий тебя пункт.'
        list_tasks = ['/Новая_запись']
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    markup.add(*list_tasks)
    bot.send_message(message.chat.id, text, reply_markup=markup)


@bot.message_handler(commands=['Новая_запись'])
def start_record(message):
    """Новая запись."""
    global count
    global answer
    markup = types.InlineKeyboardMarkup(row_width=1)
    button = [types.InlineKeyboardButton(text='Давай начнем запись', callback_data='start')]
    markup.add(*button)
    text = f'Я помогу тебе записаться.'
    message_to_edit = bot.send_message(message.chat.id, text, reply_markup=markup, parse_mode='HTML')
    count += 1
    while count != answer:
        time.sleep(5)
    bot.edit_message_reply_markup(chat_id=message_to_edit.chat.id, message_id=message_to_edit.message_id)
    step_name(message)


def step_name(message):
    """Заполнение имени."""
    global count
    text = "Пришли имя и фамилию!\n❗️ Внимание: отправь в данном сообщении ИМЯ и ФАМИЛИЮ того, кто хочется записаться " \
           "на встречу(как в паспорте).\nНе нужно отправлять в одном сообщении телефон, почту и другую информацию! " \
           "Она будет запрошена далее. "
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    button = [f'{message.chat.first_name} {message.chat.last_name}', '/Отмена']
    markup.add(*button)
    count += 1
    bot.send_message(message.chat.id, text, reply_markup=markup)


def step_phone(message):
    """Заполение контактного номера."""
    global count
    keyboard = types.ReplyKeyboardMarkup(row_width=1, one_time_keyboard=True, resize_keyboard=True)
    button_phone = types.KeyboardButton(text="Отправить телефон", request_contact=True)
    button = [button_phone, '/Отмена']
    keyboard.add(*button)
    text = 'Пришли номер телефона, либо поделись им, нажав на кнопку! (номера принимаются в формате 79998887766)'
    count += 1
    bot.send_message(message.chat.id, text, reply_markup=keyboard)


def country(message):
    """Выбор страны."""
    global count
    list_country = ['UZBEKISTAN', 'KYRGYZSTAN', 'MAURITIUS', 'MOZAMBIQUE', 'Отмена']
    text = "Выбери страну для записи:"
    markup = types.InlineKeyboardMarkup(row_width=1)
    button = []
    for country in list_country:
        button.append(types.InlineKeyboardButton(text=f"{country}", callback_data=f"{country}"))
    markup.add(*button)
    messagetoedit = bot.send_message(message.chat.id, text, reply_markup=markup)
    count += 1
    while count != answer:
        time.sleep(5)
    if count == 0 and answer == 0:
        bot.edit_message_reply_markup(chat_id=messagetoedit.chat.id, message_id=messagetoedit.message_id)
        list_tasks = ['/start']
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
        markup.add(*list_tasks)
        text = 'Чтобы вернутся в главное меню - нажми /start'
        bot.send_message(message.chat.id, text, reply_markup=markup)
    else:
        bot.edit_message_reply_markup(chat_id=messagetoedit.chat.id, message_id=messagetoedit.message_id)
        answer_record(message)


def answer_record(message):
    """Отправка заполненных данных на проверку клиенту."""
    data = BotDB.get_last_record(message)
    text = (f"Запись успешно сделана. Проверь данные:\n{data[0][0]})Имя: {data[0][2]},\nФамилия: {data[0][3]},\n"
            f"Страна записи: {data[0][4]},\nКонтактный телефон: {data[0][5]}")
    bot.send_message(message.chat.id, text)
    list_tasks = ['/start']
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    markup.add(*list_tasks)
    text = 'Чтобы вернутся в главное меню - нажми /start'
    bot.send_message(message.chat.id, text, reply_markup=markup)


@bot.message_handler(commands=['Посмотреть_записи'])
def all_records(message):
    """Просмотр всех записей пользователя."""
    data = BotDB.get_record(message)
    for d in range(len(data)):
        text = (f"Ваши активные записи:\nИмя: {data[d][2]},\nФамилия: {data[d][3]},\nСтрана записи: {data[d][4]},"
                f"\nКонтактный телефон: {data[d][5]}\nId записи: {data[d][0]}")
        bot.send_message(message.chat.id, text)
    list_tasks = ['/start']
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    markup.add(*list_tasks)
    text = 'Чтобы вернутся в главное меню - нажми /start'
    bot.send_message(message.chat.id, text, reply_markup=markup)


@bot.message_handler(commands=['Удалить_запись'])
def drop_record(message):
    """Запрос удаления записи от пользователя."""
    global count
    text = 'Введите Id записи, которая больше не актуальна'
    sent = bot.send_message(message.chat.id, text)
    bot.register_next_step_handler(sent, drop)
    count += 1
    while count != answer:
        time.sleep(5)
    list_tasks = ['/start']
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    markup.add(*list_tasks)
    text = 'Чтобы вернутся в главное меню - нажми /start'
    bot.send_message(message.chat.id, text, reply_markup=markup)


def drop(message):
    """Обработка запроса на удаление."""
    global answer
    data = BotDB.drop(message)
    bot.send_message(message.chat.id, data)
    answer += 1


@bot.message_handler(content_types=["text", "contact"])
def get_info(message):
    """Обработка ответов пользователей."""
    global answer
    global count
    if message.contact is not None:
        BotDB.update_phone(message, message.contact.phone_number)
        answer += 1
        while count != answer:
            time.sleep(5)
        country(message)
    elif any(map(str.isdigit, message.text)):
        BotDB.update_phone(message, message.text)
        answer += 1
        while count != answer:
            time.sleep(5)
        country(message)
    else:
        id = BotDB.update_name(message)
        if id.isdigit():
            answer += 1
            while count != answer:
                time.sleep(5)
            step_phone(message)
        else:
            bot.send_message(message.chat.id, id)
            list_tasks = ['/start']
            markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
            markup.add(*list_tasks)
            text = 'Чтобы вернутся в главное меню - нажми /start'
            bot.send_message(message.chat.id, text, reply_markup=markup)


@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    """Ответ на инлайн кнопки"""
    global answer
    global count
    if call.message:
        if call.data == 'start':
            BotDB.add_user(call.message)
            answer += 1
        elif call.data == 'Отмена':
            BotDB.drop_recorde(call.message)
            answer = 0
            count = 0
        elif call.data in ['UZBEKISTAN', 'KYRGYZSTAN', 'MAURITIUS', 'MAURITIUS', 'MOZAMBIQUE']:
            BotDB.update_country(call.message, call.data)
            answer += 1


def main():
    """Основная логика работы бота."""
    while True:
        try:
            # BotDB.new_table()
            # BotDB.drop_table()
            bot.polling(none_stop=True, interval=0)
        except Exception as error:
            print(error)
            time.sleep(5)
            continue


if __name__ == '__main__':
    logging.basicConfig(
        level=logging.DEBUG,
        filename='program.log',
        format='%(asctime)s, %(levelname)s, %(message)s'
    )
    main()
