#!/usr/bin/env python
# -*- coding: utf-8 -*-

from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters, RegexHandler,
                          ConversationHandler)

import logging

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

CHOOSING, LOG_IN, CHOOSE_DESTINATION, FILTER_AND_SELECT, CHECK_PERSONAL_INFO, CONFIRMATION, ASK_INFO, CONFIRM_ACCOUNT_INFO = range(8)

main_keyboard = [['Book'], 
                 ['Manage Bookings'],
                 ['Log in']]
yesno_keyboard = [['Yes'],
                  ['No']]
filter_keyboard = [['Por fecha'], 
                   ['Por precio'], 
                   ['Fechas más baratas']]
main_markup = ReplyKeyboardMarkup(main_keyboard, one_time_keyboard=True)
yesno_markup = ReplyKeyboardMarkup(yesno_keyboard, one_time_keyboard=True)
filter_markup = ReplyKeyboardMarkup(filter_keyboard, one_time_keyboard=True)

def facts_to_str(user_data):
    facts = list()

    for key, value in user_data.items():
        facts.append('{} - {}'.format(key, value))

    return "\n".join(facts).join(['\n', '\n'])


def start(bot, update):
    update.message.reply_text(
        "Hi! My name is Tamagochi."
        "How can I help you?",
        reply_markup=main_markup)

    return CHOOSING

def log_in(bot, update, user_data):
    update.message.reply_text('Logging in...')
    # OAUTH
    user_data['token'] = '1234'
    update.message.reply_text('OK! What do you want to do now?', reply_markup=main_markup)
    return CHOOSING

def regular_choice(bot, update, user_data):
    text = update.message.text
    user_data['choice'] = text
    if text == 'Book':
        update.message.reply_text('Type where and when you want to go')
        return CHOOSE_DESTINATION
    elif text == 'Manage Bookings':
        # To do
        return CHOOSE_DESTINATION
    else:
        update.message.reply_text('Type your credentials')
        return LOG_IN
    
def nl_to_dispo(bot, update, user_data):
    text = update.message.text
    user_data['nl_message'] = text
    update.message.reply_text('Querying results for"{}"'.format(text))
    # Get info with NLP
    # Ask API
    user_data['response'] = '/1 Destino 1 \n /2 Destino 2' #Api response
    update.message.reply_text('Reply:\n {}'.format(user_data['response']))
    update.message.reply_text('Select an option or filter the results:', reply_markup=filter_markup)
    return FILTER_AND_SELECT

def filter(bot, update, user_data):
    # Filter results
    new_results = user_data['response']
    update.message.reply_text('Reply:\n {}'.format(new_results))
    update.message.reply_text('Select an option or filter the results:', reply_markup=filter_markup)
    return FILTER_AND_SELECT

def select_from_dispo(bot, update, user_data):
    update.message.reply_text('Selected option {}'.format(update.message.text))
    if 'token' in user_data.keys():
        update.message.reply_text('Do you want to book with your account stored information?\nName:xx,\n ...', reply_markup=yesno_markup)
        user_data['data'] = 'Some user data'
        return CONFIRM_ACCOUNT_INFO
    else:
        update.message.reply_text('Please enter your information:', reply_markup = ReplyKeyboardRemove())
        return ASK_INFO

def confirm_account_info(bot, update, user_data):
    text = update.message.text
    if text == 'Yes':
        confirm(update, user_data['data'])
        return CONFIRMATION
    else:
        update.message.reply_text('Please enter your information:', reply_markup = ReplyKeyboardRemove())
        return ASK_INFO

def parse_user_info(bot, update, user_data):
    user_data['data'] = update.message.text
    confirm(update, user_data['data'])
    return CONFIRMATION

def book(bot, update, user_data):
    update.message.reply_text('Booking')
    # Book using API
    update.message.reply_text('Booking successful', reply_markup = main_markup)
    return CHOOSING

def confirm(update, info):
    update.message.reply_text('Confirm with info: info info info', reply_markup=yesno_markup)

def done(bot, update, user_data):
    if 'choice' in user_data:
        del user_data['choice']

    update.message.reply_text("I learned these facts about you:"
                              "{}"
                              "Until next time!".format(facts_to_str(user_data)))

    user_data.clear()
    return ConversationHandler.END

def error(bot, update, error):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, error)


def main():
    # Create the Updater and pass it your bot's token.
    updater = Updater(token="537393200:AAEoMW2iuH1SUjkZt5PoVeo6sPQDZuNJheo")

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # Add conversation handler with the states GENDER, PHOTO, LOCATION and BIO
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],

        states={
            CHOOSING: [RegexHandler('^(Book|Manage bookings|Log in)$',
                                    regular_choice,
                                    pass_user_data=True),
                       MessageHandler(Filters.text,
                                      nl_to_dispo,
                                      pass_user_data=True),
                       ],
            LOG_IN: [MessageHandler(Filters.text,
                                    log_in,
                                    pass_user_data=True),
                    ],
            CHOOSE_DESTINATION: [MessageHandler(Filters.text,
                                                nl_to_dispo,
                                                pass_user_data=True),
                                ],
            FILTER_AND_SELECT: [CommandHandler('1', select_from_dispo, pass_user_data=True),
                                CommandHandler('2', select_from_dispo, pass_user_data=True),
                                CommandHandler('3', select_from_dispo, pass_user_data=True),
                                CommandHandler('4', select_from_dispo, pass_user_data=True),
                                CommandHandler('5', select_from_dispo, pass_user_data=True),
                                RegexHandler('^(Por fecha|Por precio|Fechas más baratas)$', 
                                             filter, 
                                             pass_user_data=True)
                               ],
            CONFIRM_ACCOUNT_INFO: [RegexHandler('^(Yes|No)$', confirm_account_info, pass_user_data = True)],
            ASK_INFO: [MessageHandler(Filters.text, 
                                      parse_user_info, 
                                      pass_user_data = True)
                      ],
            
            CONFIRMATION: [RegexHandler('^(Yes|No)$', book, pass_user_data = True)],
        },

        fallbacks=[RegexHandler('^Done$', done, pass_user_data=True)]
    )

    dp.add_handler(conv_handler)

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
