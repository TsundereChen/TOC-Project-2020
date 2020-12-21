from linebot import LineBotApi
from linebot.models import TextSendMessage, ImageSendMessage
from linebot.exceptions import LineBotApiError

from config import channel_secret, channel_access_token

lineBotApi = LineBotApi(channel_access_token)

def webhook_parser(webhook):
    event = webhook["events"][0]
    replyToken = event["replyToken"]
    userId = event["source"]["userId"]
    message = event["message"]["text"]

    return replyToken, userId, message

class LineAPI:
    @staticmethod
    def sendReplyMessage(replyToken, replyMessage):
        try:
            lineBotApi.reply_message(replyToken, TextSendMessage(replyMessage))
        except LineBotApiError:
            print(LineBotApiError)
