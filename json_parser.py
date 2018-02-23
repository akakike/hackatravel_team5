import json
import telegram


def parse_dispo(text, bot, update, user_data):


    data = json.loads(text)
    user_data['response'] = ''
    i = 1
    for dispo_item in data:
        response = '/{} '.format(i)
        response += '[#]({})'.format(dispo_item['image'])
        response += dispo_item['name']
        if 'duration' in dispo_item.keys():
            response += ' ({}) '.format(dispo_item['duration'])
        if 'duration' in dispo_item.keys():
            response += dispo_item['type']
        response += '. Price: {} - {}€'.format(dispo_item['priceFrom'], dispo_item['priceTo'])
        response += '\n'
        user_data['response'] += response
        bot.send_message(chat_id=update.message.chat_id, text='{}'.format(response), parse_mode=telegram.ParseMode.MARKDOWN)

        i = i + 1
    return response
