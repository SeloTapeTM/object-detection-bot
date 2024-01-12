import flask
from flask import request
import os
from bot.bot import Bot, ImageProcessingBot # ObjectDetectionBot, QuoteBot

app = flask.Flask(__name__)

TELEGRAM_TOKEN_FILE = os.environ['TELEGRAM_TOKEN_FILE']  # TELEGRAM_TOKEN = os.environ['TELEGRAM_TOKEN']
with open(TELEGRAM_TOKEN_FILE, 'r') as file:
    TELEGRAM_TOKEN = file.read().rstrip()

TELEGRAM_APP_URL_FILE = os.environ['TELEGRAM_APP_URL_FILE']  # TELEGRAM_APP_URL = os.environ['TELEGRAM_APP_URL']
with open(TELEGRAM_APP_URL_FILE, 'r') as file:
    TELEGRAM_APP_URL = file.read().rstrip()

BUCKET_NAME_FILE = os.environ['BUCKET_NAME_FILE']  # BUCKET_NAME = os.environ['BUCKET_NAME']
with open(BUCKET_NAME_FILE, 'r') as file:
    BUCKET_NAME = file.read().rstrip()

YOLO5_CONT_NAME = os.environ['YOLO5_CONT_NAME']


@app.route('/', methods=['GET'])
def index():
    return 'Ok'


@app.route(f'/{TELEGRAM_TOKEN}/', methods=['POST'])
def webhook():
    req = request.get_json()
    bot.handle_message(req['message'])
    return 'Ok'


if __name__ == "__main__":
    bot = ImageProcessingBot(TELEGRAM_TOKEN, TELEGRAM_APP_URL, BUCKET_NAME, YOLO5_CONT_NAME)

    app.run(host='0.0.0.0', port=8443)


