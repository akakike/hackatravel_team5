import requests
from json_parser import parse_dispo

def call(endpoint, params=None):
    return """
    [
   {
       "duration": "Full day",
       "image": "http://media.activitiesbank.com/32802/ENG/S/32802_3.jpg",
       "name": "Aquatica Meal Deal",
       "priceFrom": 12.86,
       "priceTo": 21.45,
       "target": "Families",
       "type": "Theme and water parks"
   },
   {
       "duration": "Full day",
       "image": "http://media.activitiesbank.com/13684/ENG/S/13684_2.jpg",
       "name": "Legoland Florida",
       "priceFrom": 64.47,
       "priceTo": 59.61,
       "target": "Families",
       "type": "Theme and water parks"
   },
   {
       "duration": "Flexible",
       "image": "http://media.activitiesbank.com/28252/ENG/S/28252_4.jpg",
       "name": "ATV off-road experience",
       "priceFrom": 75.4,
       "priceTo": 75.4,
       "target": "Youth",
       "type": "Tours & Activities"
   },
   {
       "duration": "Full day",
       "image": "http://media.activitiesbank.com/16406/ENG/S/16406_4.jpg",
       "name": "Adventures in the Wild",
       "priceFrom": 26.54,
       "priceTo": 18.3,
       "target": "Youth",
       "type": "Tours & Activities"
   },
   {
       "duration": "Full day",
       "image": "http://media.activitiesbank.com/30362/ENG/S/30362_2.jpg",
       "name": "Airboat and monster truck ride",
       "priceFrom": 78.4,
       "priceTo": 66.07,
       "target": "Families",
       "type": "Tours & Activities"
   }
]
    """
    # Create http request and add headers
    headers = {'Accept': 'application/json', 'Content-Type': 'application/json'}

    # Reading response and print-out
    response = requests.post(endpoint, json=params, headers=headers)
    return response.content


def avail(bot, update, user_data, data):
    update.message.reply_text('Querying results for"{}"'.format(data))

    res = call('http://localhost:5000/avail')
    parse_dispo(res, bot, update, user_data)


def avail_location(bot, update, user_data, data):
    return avail(bot, update, user_data, data)

