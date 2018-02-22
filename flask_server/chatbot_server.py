from flask import Flask
from flask import request
import api_client
import json
from flask.json import jsonify

app = Flask(__name__)


class AvailRS(object):
    def __init__(self, data):
        self.__dict__ = json.loads(data)


@app.route("/avail", methods=['POST'])
def avail():
    avail_response = api_client.avail_destination('MCO')
    avail_json = AvailRS(avail_response)

    result = []

    for activity_result in avail_json.activities:
        activity_item = activity_result
        item = {
            'name': activity_item["name"],
            'priceFrom': activity_item["amountsFrom"][0]["amount"],
            'priceTo': activity_item["amountsFrom"][len(activity_item["amountsFrom"])-1]["amount"]
        }
        if len(activity_item["content"]["segmentationGroups"]) > 0:
            for segmentationGroup in activity_item["content"]["segmentationGroups"]:
                if segmentationGroup["code"] == 1:
                    item["type"] = segmentationGroup["segments"][0]["name"]
                if segmentationGroup["code"] == 2:
                    item["target"] = segmentationGroup["segments"][0]["name"]
                if segmentationGroup["code"] == 3:
                    item["duration"] = segmentationGroup["segments"][0]["name"]

        item["image"] = activity_item["content"]["media"]["images"][0]["urls"][0]["resource"]

        result.append(item)

    return jsonify(result)

@app.route("/booking/confirm", methods=['POST'])
def confirm():
    values = request.get_json()
    rateKey = values['rateKey']
    date_from = values['from']
    date_to = values['to']
    return api_client.booking_confirm(rateKey, date_from, date_to)


@app.route("/booking/cancel/<reference>", methods=['DELETE'])
def cancel(reference):
    return api_client.booking_cancel(reference)


if __name__ == "__main__":
    app.run()
