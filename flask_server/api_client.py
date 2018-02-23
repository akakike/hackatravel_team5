import time, hashlib
import requests

# Your API Key and secret
apiKey = "pe6ud6vswhta6a49epk356kz"
Secret = "t7WVC5ukk7"

# Signature is generated by SHA256 (Api-Key + Secret + Timestamp (in seconds))
sigStr = "%s%s%d" % (apiKey, Secret, int(time.time()))
signature = hashlib.sha256(sigStr.encode()).hexdigest()


def call(endpoint, params=None):

    # Create http request and add headers
    headers = {'X-Signature': signature, 'Api-Key': apiKey, 'Accept': 'application/json', 'Content-Type': 'application/json'}

    # Reading response and print-out
    response = requests.post(endpoint, json=params, headers=headers)

    return response.content


def avail_destination(destination_code, date_from, date_to):
    params = {
      'filters': [
            {
                'searchFilterItems': [
                    {'type': 'destination', 'value': destination_code}
                ]

            }
      ],
      'from': date_from,
      'to': date_to,
      'language': 'en',
      'pagination': {
        'itemsPerPage': 10,
        'page': 1
      },
      'order': 'DEFAULT'
    }

    return call("https://api.test.hotelbeds.com/activity-api/3.0/activities", params)


def detail(activity_code, date_from, date_to):
    params = {
        "code": activity_code,
        "from": date_from,
        "to": date_to,
        "language": "en",
        "paxes": [
            {"age": 30},
            {"age": 30}
        ]
    }

    return call("https://api.test.hotelbeds.com/activity-api/3.0/activities/details", params)


def booking_confirm(rateKey, date_from, date_to):
    params = {
          "language": "en",
          "clientReference": "Agency test",
          "holder": {
            "name": "TestHolder",
            "email": "testholder@hotelbeds.com",
            "surname": "Test",
            "telephones": [
              "123456789"
            ]
          },
          "activities": [
            {
              "preferedLanguage": "en",
              "serviceLanguage": "en",
              "rateKey": rateKey,
              "from": date_from,
              "to": date_to,
              "paxes": [
                {
                  "age": 30,
                  "name": "TestPax1",
                  "type": "ADULT",
                  "surname": "Test"
                },
                {
                  "age": 30,
                  "name": "TestPax2",
                  "type": "ADULT",
                  "surname": "Test"
                }
              ]
            }
          ]
        }
    return call("https://api.test.hotelbeds.com/activity-api/3.0/bookings", params)


def booking_cancel(reference):
    return call("https://api.test.hotelbeds.com/activity-api/3.0/bookings/en/" + reference)