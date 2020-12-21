import os
from flask import Flask, jsonify, request, abort, send_file
from linebot import LineBotApi, WebhookParser
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
import json

from config import channel_access_token, channel_secret

from fsm import TocMachine
from line import webhook_parser, LineAPI

machines = {}

app = Flask(__name__, static_url_path="")

def inputHandler(machineState, replyToken, userId, message):
    app.logger.info(f"Handling state: {machineState}")
    if machineState == "init":
        machines[userId].advance(replyToken, message)
    if machineState == "options":
        machines[userId].chooseOption(replyToken, message)
    if machineState == "latestCheck":
        machines[userId].enterLatestPrice(replyToken, message)
    if machineState == "historicalCheck":
        machines[userId].enterHistoricalPrice(replyToken, message)
    if machineState == "latestPrice":
        machines[userId].goNewsOrGoBack(replyToken, message)
    if machineState == "historicalPrice":
        machines[userId].goNewsOrGoBack(replyToken, message)
    if machineState == "newsCheck":
        machines[userId].enterNews(replyToken, message)

@app.route("/", methods=["GET"])
def working():
    return "The bot is working!"

@app.route("/webhook", methods=["POST"])
def webhook_handler():
    webhook = json.loads(request.data.decode("utf-8"))
    replyToken, userId, message = webhook_parser(webhook)

    app.logger.info(f"Reply Token: {replyToken}")
    app.logger.info(f"User ID: {userId}")
    app.logger.info(f"Message: {message}")

    if userId not in machines:
        machines[userId] = TocMachine()

    inputHandler(machines[userId].state, replyToken, userId, message)
    return jsonify({})

@app.route("/show-fsm", methods=["GET"])
def show_fsm():
    machine = TocMachine()
    machine.get_graph().draw("fsm.png", prog="dot", format="png")
    return send_file("fsm.png", mimetype="image/png")


if __name__ == "__main__":
    port = os.environ.get("PORT", 8000)
    app.run(host="0.0.0.0", port=port, debug=True)
