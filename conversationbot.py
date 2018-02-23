#!/usr/bin/env python
# -*- coding: utf-8 -*-

from telegram import KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters, RegexHandler,
                          ConversationHandler)
import telegram
import request_interpreter as nlp
import conversation_api
import conversation_pax
import conversation_actions
import conversation_helper
import logging

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

main_keyboard = [['Book'],
                 ['Near me'],
                 ['Log in']]
yesno_keyboard = [['Yes'],
                  ['No']]
yesnopaxes_keyboard = [['Yes'], ['No'], ['Add Pax'], ['Other People']]
filter_keyboard = [['Date'],
                   ['Price'],
                   ['Cheapest dates']]
main_markup = ReplyKeyboardMarkup(main_keyboard, one_time_keyboard=True)
yesno_markup = ReplyKeyboardMarkup(yesno_keyboard, one_time_keyboard=True)
yesnopaxes_markup = ReplyKeyboardMarkup(yesnopaxes_keyboard, one_time_keyboard=True)
filter_markup = ReplyKeyboardMarkup(filter_keyboard, one_time_keyboard=True)


def reset(bot, update):
    update.message.reply_text("Let's restart", reply_markup=main_markup)
    return conversation_actions.CHOOSING


def start(bot, update):
    update.message.reply_text(
        "Hi! My name is Hack@Travel."
        "How can I help you?",
        reply_markup=main_markup)

    return conversation_actions.CHOOSING


def log_in(bot, update, user_data):
    update.message.reply_text('Logging in...')
    # OAUTH

    user_data['token'] = '1234'
    user_data['paxes'] = []
    user_data['paxes'].append({'name': 'John Doe', 'age': 45})
    update.message.reply_text('Hi John,', reply_markup=main_markup)
    update.message.reply_text('Write your search or select in buttons below', reply_markup=main_markup)

    return conversation_actions.CHOOSING


def regular_choice(bot, update, user_data):
    text = update.message.text
    user_data['choice'] = text
    if text == 'Book':
        update.message.reply_text('Type where and when you want to go')
        return conversation_actions.CHOOSE_DESTINATION
    elif text == 'Near me':
        location_keyboard = KeyboardButton(text="Send location", request_location=True)
        markup = ReplyKeyboardMarkup([[location_keyboard]])
        update.message.reply_text('Please send your location:', reply_markup=markup)
        return conversation_actions.SEARCH_BY_LOCATION
    else:
        update.message.reply_text('Type your credentials')
        return conversation_actions.LOG_IN


def search_by_location(bot, update, user_data):
    user_data['location'] = update.message.location
    # Get area offers by area from API
    conversation_api.avail_location(bot, update, user_data, user_data['location'])

    update.message.reply_text('Select an option or filter the results:', reply_markup=filter_markup)
    return conversation_actions.FILTER_AND_SELECT


def nl_to_dispo(bot, update, user_data):
    text = update.message.text
    user_data['nl_message'] = text
    parsed_text = nlp.translate_human_request(text)

    conversation_api.avail(bot, update, user_data, parsed_text)

    update.message.reply_text('Select an option or filter the results:', reply_markup=filter_markup)
    return conversation_actions.FILTER_AND_SELECT


def filter(bot, update, user_data):
    text = update.message.text
    user_data['filter'] = text
    if text == "Date":
        update.message.reply_text('What dates do you want?')
    elif text == "Price":
        update.message.reply_text('Enter a price:')
    else:
        apply_filter(bot, update, user_data)
    return conversation_actions.FILTER


def apply_filter(bot, update, user_data):
    text = update.message.text
    command = user_data['filter']
    data = nlp.translate_human_request(text)
    # if command == "Date":

    # elif command == "Price":

    # else:

    conversation_api.avail(bot, update, user_data)

    update.message.reply_text('Select an option or filter the results:', reply_markup=filter_markup)
    return conversation_actions.FILTER_AND_SELECT


def select_from_dispo(bot, update, user_data):
    bot.send_message(chat_id=update.message.chat_id,
                     text='{}'.format(user_data['response'][int(update.message.text[1]) - 1][2:]),
                     parse_mode=telegram.ParseMode.MARKDOWN)
    user_data['selected'] = int(update.message.text[1]) - 1

    if 'token' in user_data.keys():
        update.message.reply_text('Do you want to book with your account stored information?\n',
                                  reply_markup=yesnopaxes_markup)
        conversation_pax.print_pax_info(bot, update, user_data)
        return conversation_actions.CONFIRM_ACCOUNT_INFO
    else:
        update.message.reply_text('Please enter your full name:', reply_markup=ReplyKeyboardRemove())
        return conversation_actions.ASK_INFO


def confirm_account_info(bot, update, user_data):
    text = update.message.text
    if text == 'Yes':
        confirm(bot, update, user_data)
        return conversation_actions.CONFIRMATION
    if text == 'No':
        update.message.reply_text('Please enter your full name:', reply_markup=ReplyKeyboardRemove())
        return conversation_actions.ASK_INFO
    if text == 'Add Pax':
        conversation_pax.add_pax(user_data)
        update.message.reply_text('Please enter your full name:', reply_markup=ReplyKeyboardRemove())
        return conversation_actions.ASK_INFO
    if text == 'Other People':
        conversation_pax.reset_paxes(user_data)
        update.message.reply_text('Please enter your full name:', reply_markup=ReplyKeyboardRemove())
        return conversation_actions.ASK_INFO


def parse_user_info(bot, update, user_data):
    conversation_pax.set_name_to_current_pax(user_data, update.message.text)
    update.message.reply_text('Please enter your age:', reply_markup=ReplyKeyboardRemove())
    return conversation_actions.ASK_AGE


def parse_user_age(bot, update, user_data):
    conversation_pax.set_age_to_current_pax(user_data, update.message.text)
    confirm(bot, update, user_data)
    return conversation_actions.CONFIRMATION


def book(bot, update, user_data):
    text = update.message.text
    if text == 'Yes':
        update.message.reply_text('Booking')
        conversation_api.book(bot, update, user_data)
        # Book using API
        update.message.reply_text('Booking successful', reply_markup=main_markup)
        return conversation_actions.CHOOSING
    if text == 'No':
        update.message.reply_text('Cancelling..', reply_markup=main_markup)
        return conversation_actions.CHOOSING
    if text == 'Add Pax':
        conversation_pax.add_pax(user_data)
        update.message.reply_text('Please enter your full name:', reply_markup=ReplyKeyboardRemove())
        return conversation_actions.ASK_INFO
    if text == 'Other People':
        conversation_pax.reset_paxes(user_data)
        update.message.reply_text('Please enter your full name:', reply_markup=ReplyKeyboardRemove())
        return conversation_actions.ASK_INFO


def confirm(bot, update, user_data):
    update.message.reply_text('Confirm with info: ', reply_markup=yesnopaxes_markup)
    conversation_pax.print_pax_info(bot, update, user_data)


def main():
    # Create the Updater and pass it your bot's token.
    updater = Updater(token="537393200:AAEoMW2iuH1SUjkZt5PoVeo6sPQDZuNJheo")

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # Add conversation handler with the states GENDER, PHOTO, LOCATION and BIO
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start), CommandHandler('reset', reset)],

        states={
            conversation_actions.CHOOSING: [RegexHandler('^(Book|Near me|Log in)$',
                                                         regular_choice,
                                                         pass_user_data=True),
                                            MessageHandler(Filters.text,
                                                           nl_to_dispo,
                                                           pass_user_data=True),
                                            ],
            conversation_actions.LOG_IN: [MessageHandler(Filters.text,
                                                         log_in,
                                                         pass_user_data=True),
                                          ],
            conversation_actions.CHOOSE_DESTINATION: [MessageHandler(Filters.text,
                                                                     nl_to_dispo,
                                                                     pass_user_data=True),
                                                      ],
            conversation_actions.SEARCH_BY_LOCATION: [
                MessageHandler(Filters.location, search_by_location, pass_user_data=True)],
            conversation_actions.FILTER_AND_SELECT: [CommandHandler('1', select_from_dispo, pass_user_data=True),
                                                     CommandHandler('2', select_from_dispo, pass_user_data=True),
                                                     CommandHandler('3', select_from_dispo, pass_user_data=True),
                                                     CommandHandler('4', select_from_dispo, pass_user_data=True),
                                                     CommandHandler('5', select_from_dispo, pass_user_data=True),
                                                     CommandHandler('6', select_from_dispo, pass_user_data=True),
                                                     CommandHandler('7', select_from_dispo, pass_user_data=True),
                                                     CommandHandler('8', select_from_dispo, pass_user_data=True),
                                                     CommandHandler('9', select_from_dispo, pass_user_data=True),
                                                     CommandHandler('10', select_from_dispo, pass_user_data=True),
                                                     RegexHandler('^(Date|Price|Cheapest dates)$',
                                                                  filter,
                                                                  pass_user_data=True)
                                                     ],
            conversation_actions.FILTER: [MessageHandler(Filters.text, apply_filter, pass_user_data=True)],
            conversation_actions.CONFIRM_ACCOUNT_INFO: [
                RegexHandler('^(Yes|No|Add Pax|Other People)$', confirm_account_info, pass_user_data=True)],
            conversation_actions.ASK_INFO: [MessageHandler(Filters.text,
                                                           parse_user_info,
                                                           pass_user_data=True)
                                            ],
            conversation_actions.ASK_AGE: [MessageHandler(Filters.text,
                                                          parse_user_age,
                                                          pass_user_data=True)
                                           ],
            conversation_actions.CONFIRMATION: [
                RegexHandler('^(Yes|No|Add Pax|Other People)$', book, pass_user_data=True)],
        },

        fallbacks=[RegexHandler('^Done$', conversation_helper.done, pass_user_data=True),
                   MessageHandler(Filters.location, search_by_location, pass_user_data=True)
                   ],

        allow_reentry=True
    )

    dp.add_handler(conv_handler)

    # log all errors
    dp.add_error_handler(conversation_helper.error)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
