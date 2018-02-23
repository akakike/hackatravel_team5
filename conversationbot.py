#!/usr/bin/env python
# -*- coding: utf-8 -*-

from telegram import KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters, RegexHandler,
                          ConversationHandler)
import request_interpreter as nlp
import logging
import requests

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

CHOOSING, LOG_IN, CHOOSE_DESTINATION, SEARCH_BY_LOCATION, FILTER_AND_SELECT, FILTER, CHECK_PERSONAL_INFO, CONFIRMATION, ASK_INFO, CONFIRM_ACCOUNT_INFO = range(10)

main_keyboard = [['Book'], 
                 ['Near me'],
                 ['Log in']]
yesno_keyboard = [['Yes'],
                  ['No']]
filter_keyboard = [['Date'], 
                   ['Price'], 
                   ['Cheapest dates']]
main_markup = ReplyKeyboardMarkup(main_keyboard, one_time_keyboard=True)
yesno_markup = ReplyKeyboardMarkup(yesno_keyboard, one_time_keyboard=True)
filter_markup = ReplyKeyboardMarkup(filter_keyboard, one_time_keyboard=True)

def call(endpoint, params=None):

    # Create http request and add headers
    headers = {'Accept': 'application/json', 'Content-Type': 'application/json'}

    # Reading response and print-out
    response = requests.post(endpoint, json=params, headers=headers)
    return response.content

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
    r = call('http://localhost:5000/avail')

    user_data['token'] = '1234'
    update.message.reply_text('OK! What do you want to do now? {}'.format(r), reply_markup=main_markup)
    return CHOOSING

def regular_choice(bot, update, user_data):
    text = update.message.text
    user_data['choice'] = text
    if text == 'Book':
        update.message.reply_text('Type where and when you want to go')
        return CHOOSE_DESTINATION
    elif text == 'Near me':
        location_keyboard = KeyboardButton(text="Send location", request_location=True)
        markup = ReplyKeyboardMarkup([[location_keyboard]])
        update.message.reply_text('Please send your location:', reply_markup = markup)
        return SEARCH_BY_LOCATION
    else:
        update.message.reply_text('Type your credentials')
        return LOG_IN
    
def search_by_location(bot, update, user_data):
    user_data['location'] = update.message.location
    # Get area offers by area from API
    user_data['response'] = '/1 Destino 1 \n /2 Destino 2' #Api response
    update.message.reply_text('Reply for {}, {}:\n {}'.format(user_data['location'].longitude,
                                                              user_data['location'].latitude,
                                                              user_data['response']))
    update.message.reply_text('Select an option or filter the results:', reply_markup=filter_markup)
    return FILTER_AND_SELECT

def nl_to_dispo(bot, update, user_data):
    text = update.message.text
    user_data['nl_message'] = text
    parsed_text = nlp.translate_human_request(text)
    update.message.reply_text('Querying results for"{}"'.format(parsed_text))
    # Get info with NLP
    # Ask API
    user_data['response'] = '/1 Destino 1 \n /2 Destino 2' #Api response
    update.message.reply_text('Reply:\n {}'.format(user_data['response']))
    update.message.reply_text('Select an option or filter the results:', reply_markup=filter_markup)
    return FILTER_AND_SELECT

def filter(bot, update, user_data):
    text = update.message.text
    user_data['filter'] = text
    if text == "Date":
        update.message.reply_text('What dates do you want?')
    elif text == "Price":
        update.message.reply_text('Enter a price:')
    else:
        apply_filter(bot, update, user_data)
    return FILTER

def apply_filter(bot, update, user_data):
    text = update.message.text
    command = user_data['filter']
    data = nlp.translate_human_request(text)
    #if command == "Date":
        
    #elif command == "Price":
        
    #else:
        
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
    text = update.message.text
    if text == 'Yes':
        update.message.reply_text('Booking')
        # Book using API
        update.message.reply_text('Booking successful', reply_markup = main_markup)
    else:
        update.message.reply_text('Cancelling..', reply_markup = main_markup)
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
            CHOOSING: [RegexHandler('^(Book|Near me|Log in)$',
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
            SEARCH_BY_LOCATION: [MessageHandler(Filters.location, search_by_location, pass_user_data = True)],
            FILTER_AND_SELECT: [CommandHandler('1', select_from_dispo, pass_user_data=True),
                                CommandHandler('2', select_from_dispo, pass_user_data=True),
                                CommandHandler('3', select_from_dispo, pass_user_data=True),
                                CommandHandler('4', select_from_dispo, pass_user_data=True),
                                CommandHandler('5', select_from_dispo, pass_user_data=True),
                                RegexHandler('^(Date|Price|Cheapest dates)$',
                                             filter, 
                                             pass_user_data=True)
                                ],
            FILTER: [MessageHandler(Filters.text, apply_filter, pass_user_data = True)],
            CONFIRM_ACCOUNT_INFO: [RegexHandler('^(Yes|No)$', confirm_account_info, pass_user_data = True)],
            ASK_INFO: [MessageHandler(Filters.text, 
                                      parse_user_info, 
                                      pass_user_data = True)
                      ],
            
            CONFIRMATION: [RegexHandler('^(Yes|No)$', book, pass_user_data = True)],
        },

        fallbacks=[RegexHandler('^Done$', done, pass_user_data=True),
                   MessageHandler(Filters.location, search_by_location, pass_user_data = True)
                  ]
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
