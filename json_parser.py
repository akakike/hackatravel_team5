import json
import telegram


def parse_dispo(text, bot, update, user_data):
    data = json.loads(text)
    user_data['response'] = []
    user_data['options'] = data
    i = 1
    for dispo_item in data:
        response = '/{} '.format(i)
        if 'image' in dispo_item.keys():
            response += '{} [(#)]({})'.format(dispo_item['name'], dispo_item['image'])
        else:
            response += dispo_item['name']
        if 'duration' in dispo_item.keys():
            response += ' ({}) '.format(dispo_item['duration'])
        if 'duration' in dispo_item.keys():
            response += dispo_item['type']
        if int(dispo_item['priceFrom']) >= int(dispo_item['priceTo']):
            price1 = dispo_item['priceTo']
            price2 = dispo_item['priceFrom']
        else:
            price1 = dispo_item['priceFrom']
            price2 = dispo_item['priceTo']
        response += '. Price: {} - {}€'.format(price1, price2)
        response += '\n'
        user_data['response'].append(response)
        bot.send_message(chat_id=update.message.chat_id, text='{}'.format(response), parse_mode=telegram.ParseMode.MARKDOWN)

        i = i + 1
    return response
