import api_client
import chatbot_server
import json


class AvailRS(object):
    def __init__(self, data):
        self.__dict__ = json.loads(data)


print chatbot_server.hello()
