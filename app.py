"""
Copyrights ©
Licensed by GNU GPL v3.0
Created date:       17 february 2018, 02:54
Project:            InstaGain Telegram Bot
Created by:         Bionic Inc
Official site:      https://flionic.com
Required Environment variables:
    token               # Telegram Bot Api Token
    admin_id            # For admin rules
    callback_chat_id    # Telegram chat id for callback info
Optional variables:
    test_mode = 1       # enable test mode
"""
# -*- coding: utf-8 -*-
import requests
import logging
from os import environ

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ParseMode
from telegram.ext import Updater, CallbackQueryHandler
from telegram.ext import CommandHandler, MessageHandler, Filters
from telegram.error import InvalidToken

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s' if environ.get('test_mode')
    else '%(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)
chat_logs = environ.get('callback_chat_id')
md = ParseMode.MARKDOWN
print('InstaGain Telegram Bot. Copyrights © ⏤ Bionic Inc, 2018')

keys_main = [InlineKeyboardButton(" ↩️ГЛАВНОЕ МЕНЮ ↩️ ", callback_data='main_menu')]
users_data = {}


def cmd_start(bot, update):
    user = user_info(update)
    logging.info(f"User {user[1]} used /start command from chat {update.message.chat_id}")
    bot.send_message(text=f"{user[1]}\n/start", chat_id=chat_logs)  # Msg to callback chat
    bot.send_message(chat_id=update.message.chat_id, parse_mode=md,
                     text=f"Привет, {user[0]}!\nЯ создан для того, что бы сделать твой Instagram профиль популярнее 😎")
    actions(bot, update)


def cmd_unknown(bot, update):
    del_menu(bot, update, 0)
    try:
        if str(update.message.text).find("instagram.com") > 0:
            users_data.update({str(update.message.from_user.id) + '_l': update.message.text})
            bot.send_message(chat_id=update.message.chat_id, parse_mode=md,
                             text=f"Теперь укажи необходимое количество (минимум 25), или отправь новую ссылку",
                             reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(" ↩️ ГЛАВНОЕ МЕНЮ ↩️",
                                                                                      callback_data='main_menu')]]))
        elif int(str(update.message.text)) >= 25:
            users_data.update({str(update.message.from_user.id) + '_q': update.message.text})
            uid = str(update.message.from_user.id)
            params = dict(
                key='6d123fc8e9cb840f64164e82dad3c27d',
                action='create',
                service=users_data[uid + '_s'],
                quantity=users_data[uid + '_q'],
                link=users_data[uid + '_l']
            )
            resp = requests.get(url='https://nakrutka.by/api/', params=params).json()
            params = dict(
                key='6d123fc8e9cb840f64164e82dad3c27d',
                action='status',
                order=resp['order']
            )
            resp = requests.get(url='https://nakrutka.by/api/', params=params).json()
            bot.send_message(chat_id=update.message.chat_id, parse_mode=md,
                             text=f"Статус заявки: {resp['status']}",
                             reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(" ↩️ ГЛАВНОЕ МЕНЮ ↩️",
                                                                                      callback_data='main_menu')]]))
        else:
            raise ValueError
    except KeyError:
        bot.send_message(chat_id=update.message.chat_id, parse_mode=md,
                         text=f"Ошибка. Попробуйте сначала",
                         reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(" ↩️ ГЛАВНОЕ МЕНЮ ↩️",
                                                                                  callback_data='main_menu')]]))
    except ValueError:
        actions(bot, update)
    print(users_data)


def cmd_hidden(bot, update):
    bot.send_message(chat_id=update.message.chat_id, parse_mode=md,
                     text=f"© Разработчик Lisha Bionic. \nhttps://flionic.com\n")


def actions(bot, update):
    keys_services = [
        [InlineKeyboardButton("👥 Подписчики", callback_data='s_followers')],
        [InlineKeyboardButton("♥️Лайки", callback_data='s_likes')],
        [InlineKeyboardButton("💬 Комментарии", callback_data='s_comments')]
    ]
    query = update.callback_query
    if query is not None:
        del_menu(bot, query)
        #  bot.edit_message_reply_markup(query.message.chat_id, message_id=query.message.message_id)
        msg = {'keys': InlineKeyboardMarkup([[InlineKeyboardButton(" ↩️ ГЛАВНОЕ МЕНЮ ↩️", callback_data='main_menu')]]),
               'text': '', 'id': query.message.chat_id}
        if "main_menu" == query.data:
            msg['keys'] = InlineKeyboardMarkup(keys_services)
            msg['text'] = 'Выбери нужную опцию:'
        elif "s_followers" == query.data:
            msg['text'] = f'👥 Подписчики.\n\nЧто бы продолжить, дай ссылку на нужный Instagram профиль.' \
                          f'\n\nК примеру:\nhttps://instagram.com/flionic'
            users_data.update({str(query.from_user.id) + '_s': '2'})
        elif "s_likes" == query.data:
            msg['text'] = f'♥️Лайки.\n\nЧто бы продолжить, дай ссылку на нужный Instagram пост.' \
                          f'\n\nК примеру:\nhttps://www.instagram.com/p/BexPioTn5zy/'
            users_data.update({str(query.from_user.id) + '_s': '4'})
        elif "s_comments" == query.data:
            msg['text'] = f'💬 Комментарии.\n\nЧто бы продолжить, дай ссылку на нужный Instagram пост.' \
                          f'\n\nК примеру:\nhttps://www.instagram.com/p/BexPioTn5zy/'
            users_data.update({str(query.from_user.id) + '_s': '64'})
        else:
            msg['text'] = f'In the future..'
        bot.send_message(msg['id'], text=msg['text'], reply_markup=msg['keys'],
                         parse_mode=md, disable_web_page_preview=True)  # Edit message
    else:
        bot.send_message(reply_markup=InlineKeyboardMarkup(keys_services),
                         chat_id=update.message.chat_id, parse_mode=md,
                         text=f"Выбери нужную опцию:")


def user_info(update):
    user = update.message.from_user
    user.username = f' - @{user.username.replace("_", "&#95;")}' if user.username is not None else ''
    user.last_name = f' {user.last_name}' if user.last_name is not None else ''
    return [user.first_name, user.first_name + user.last_name + user.username]


def del_menu(bot, update, pl=1):
    try:
        if pl:
            bot.delete_message(update.message.chat_id, message_id=update.message.message_id)
            bot.delete_message(update.message.chat_id, message_id=update.message.message_id + 1)
        else:
            bot.delete_message(update.message.chat_id, message_id=update.message.message_id - 1)
            bot.delete_message(update.message.chat_id, message_id=update.message.message_id - 2)
    except Exception as excp:
        excp = excp


def error(bot, update, error, name=None):  # extended logger
    if name:
        logging.getLogger(name).critical(error)
        bot.send_message(chat_id=update.message.chat_id, parse_mode=md, text='Упс! Произошла ошибка 😔',
                         reply_markup=InlineKeyboardMarkup([keys_main]))  # Menu
        bot.send_message(chat_id=chat_logs, parse_mode=md, text=f'⚠️ Произошла ошибка с *{name}*\n\n{error}')
    elif update:  # Avoid duplications
        logger.warning('%s' % error)


def main():
    try:  # Create EventHandler
        updater = Updater(environ.get('token'))
        dp = updater.dispatcher
    except InvalidToken:
        logger.critical("Token is invalid")
    except ValueError:
        logger.critical("Token not given. Please, setup environment variables or check settings.py")
    else:
        # Add bot handlers
        dp.add_handler(CommandHandler('start', cmd_start))
        dp.add_handler(CommandHandler(['bionic', 'dev'], cmd_hidden))
        dp.add_handler(CallbackQueryHandler(actions))
        dp.add_handler(MessageHandler(Filters.all, cmd_unknown))
        # Extend logging
        dp.add_error_handler(error)
        # Start Bot
        logger.info("Bot launched on @%s" % updater.bot.username)
        updater.start_polling()


if __name__ == '__main__':
    main()
