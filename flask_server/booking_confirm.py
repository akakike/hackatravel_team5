from flask import Flask
from flask import request

from hackatravel_team5.flask_server import api_client

app = Flask(__name__)


@app.route("/booking/confirm",methods=['POST'])
def hello():
    values = request.get_json()
    rateKey = values['rateKey']
    date_from = values['from']
    date_to = values['to']
    return api_client.booking_confirm(rateKey, date_from, date_to)



if __name__ == "__main__":
    app.run()