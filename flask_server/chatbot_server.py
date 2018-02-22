from flask import Flask
#from . import api_client
import api_client
import json

app = Flask(__name__)


class AvailRS(object):
    def __init__(self, data):
        self.__dict__ = json.loads(data)

dictfilt = lambda x, y: dict([ (i,x[i]) for i in x if i in set(y) ])

@app.route("/")
def hello():
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

    return result

