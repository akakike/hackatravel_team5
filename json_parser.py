import json

def parse_dispo(text):
    data = json.loads(text)
    response = ''
    i = 1
    for dispo_item in data:
        response += '/{} '.format(i)
        response += dispo_item['name']
        if 'duration' in dispo_item.keys():
            response += ' ({}) '.format(dispo_item['duration'])
        if 'duration' in dispo_item.keys():
            response += dispo_item['type']
        response += '. Price: {} - {}€'.format(dispo_item['priceFrom'], dispo_item['priceTo'])
        response += '\n'
        i = i + 1
    return response
