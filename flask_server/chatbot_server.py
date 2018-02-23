from flask import Flask
from flask import request
import api_client
import json
from flask.json import jsonify

app = Flask(__name__)


class Response(object):
    def __init__(self, data):
        self.__dict__ = json.loads(data.decode("utf-8"))


@app.route("/avail", methods=['POST'])
def avail():
    values = request.get_json()
    destination = values['destination']
    date_from = values['from']
    date_to = values['to']
    avail_response = api_client.avail_destination(destination, date_from, date_to)
    avail_json = Response(avail_response)

    result = []

    for activity_result in avail_json.activities:
        activity_item = activity_result
        item = {
            'name': activity_item["name"],
            'code': activity_item["code"],
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


@app.route("/detail", methods=['POST'])
def detail():
    values = request.get_json()
    activity_code = values['activityCode']
    date_from = values['from']
    date_to = values['to']
    detail_response = api_client.detail(activity_code, date_from, date_to)
    detail_json = Response(detail_response)

    result = []

    activity = detail_json.activity
    if activity != None:
        modalities = activity['modalities']
        modality = modalities[0]
        rate = modality['rates'][0]
        rate_detail = rate['rateDetails'][0]
        operation_date = rate_detail['operationDates'][0]
        item = {
            'rateKey': rate_detail["rateKey"],
            'from': operation_date["from"],
            'to': operation_date["to"]
        }
        result.append(item)

    return jsonify(result)


@app.route("/booking/confirm", methods=['POST'])
def confirm():
    values = request.get_json()
    rateKey = values['rateKey']
    date_from = values['from']
    date_to = values['to']
    response = api_client.booking_confirm(rateKey, date_from, date_to)
    response_json = Response(response)

    result = []

    booking = response_json.booking
    if booking != None:
        item = {
            'reference': booking["reference"]
        }
        result.append(item)

    return jsonify(result)


@app.route("/booking/cancel/<reference>", methods=['DELETE'])
def cancel(reference):
    return api_client.booking_cancel(reference)


if __name__ == "__main__":
    app.run()
