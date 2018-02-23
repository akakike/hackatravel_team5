import requests
from json_parser import parse_dispo
import json
import datetime

mocked = False


def get_mocked_avail():
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


def call(endpoint, params=None):

    # Create http request and add headers
    headers = {'Accept': 'application/json', 'Content-Type': 'application/json'}

    # Reading response and print-out
    response = requests.post(endpoint, json=params, headers=headers)
    return response.content


def avail(bot, update, user_data, data):
    update.message.reply_text('Querying results for"{}"'.format(data))
    avail_rq = {
        "destination": data["places"][0],
    }
    if len(data["dates"]) > 1:
        avail_rq["from"] = data["dates"][0]
        avail_rq["to"] = data["dates"][1]
    elif len(data["dates"]) == 1:
        avail_rq["from"] = data["dates"][0]
        avail_rq["to"] = data["dates"][0]
    else:
        avail_rq["from"] = datetime.datetime.today().strftime('%Y-%m-%d')
        avail_rq["to"] = datetime.datetime.today().strftime('%Y-%m-%d')

    user_data["request"] = avail_rq

    if mocked:
        res = get_mocked_avail()
    else:
        res = call('http://localhost:5000/avail', avail_rq)
    parse_dispo(res, bot, update, user_data)


def avail_location(bot, update, user_data, data):
    avail_rq = {
        "location": {"latitude": user_data["location"]["latitude"], "longitude": user_data["location"]["longitude"]}
    }
    # if "dates" in data.keys() and len(data["dates"])>0:
    #     avail_rq["from"] = data["dates"][0]
    # else:
    avail_rq["from"] = datetime.datetime.today().strftime('%Y-%m-%d')
    # if "dates" in data.keys() and len(data["dates"])>1:
    #     avail_rq["to"] = data["dates"][1]
    # else:
    avail_rq["to"] = datetime.datetime.today().strftime('%Y-%m-%d')
    
    user_data["request"] = avail_rq

    if mocked:
        res = get_mocked_avail()
    else:
        res = call('http://localhost:5000/avail', avail_rq)
    parse_dispo(res, bot, update, user_data)



def book(bot, update, user_data):
    detail_rq = {
        "from": user_data["request"]["from"],
        "to": user_data["request"]["to"],
        "activityCode": user_data["options"][user_data["selected"]]["code"]
    }
    detail_rs = json.loads(call('http://localhost:5000/detail', detail_rq).decode("utf-8"))

    confirm_rq = {
        "from": user_data["request"]["from"],
        "to": user_data["request"]["to"],
        "rateKey": detail_rs[0]["rateKey"]
    }
    print("confir rq:{}".format(confirm_rq))
    confirm_rs = call('http://localhost:5000/booking/confirm',confirm_rq)
    print(confirm_rs)
