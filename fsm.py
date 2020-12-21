from transitions.extensions import GraphMachine

from utils import generateQueryString, queryValidChecker, priceParser, getNews

from line import LineAPI

from config import influxdb_host, influxdb_port, influxdb_username, influxdb_password
from influxdb import InfluxDBClient

client = InfluxDBClient(influxdb_host, influxdb_port, influxdb_username, influxdb_password)

class TocMachine(GraphMachine):
    def __init__(self, **machine_configs):
        self.lastCheckCurrency = "N/A"
        self.machine = GraphMachine(
                model = self,
                **{
                    "states": [
                        'init',
                        'options',
                        'latestCheck',
                        'historicalCheck',
                        'latestPrice',
                        'historicalPrice',
                        'newsCheck',
                        'news'
                    ],
                    "transitions": [
                        {
                            'trigger': 'advance',
                            'source': 'init',
                            'dest': 'options'
                        },
                        {
                            'trigger': 'chooseOption',
                            'source': 'options',
                            'dest': 'latestCheck',
                            'conditions': 'choosedLatest',
                        },
                        {
                            'trigger': 'chooseOption',
                            'source': 'options',
                            'dest': 'historicalCheck',
                            'conditions': 'choosedHistorical'
                        },
                        {
                            'trigger': 'chooseOption',
                            'source': 'options',
                            'dest': 'newsCheck',
                            'conditions': 'choosedNews'
                        },
                        {
                            'trigger': 'enterLatestPrice',
                            'source': 'latestCheck',
                            'dest': 'latestPrice',
                            'conditions': 'validCryptocurrency'
                        },
                        {
                            'trigger': 'enterLatestPrice',
                            'source': 'latestCheck',
                            'dest': 'options',
                            'conditions': 'invalidCryptocurrency'
                        },
                        {
                            'trigger': 'goNewsOrGoBack',
                            'source': 'latestPrice',
                            'dest': 'news',
                            'conditions': 'choosedNews'
                        },
                        {
                            'trigger': 'goNewsOrGoBack',
                            'source': 'latestPrice',
                            'dest': 'options',
                            'conditions': 'choosedOptions',
                        },
                        {
                            'trigger': 'enterHistoricalPrice',
                            'source': 'historicalCheck',
                            'dest': 'historicalPrice',
                            'conditions': 'validCryptocurrency'
                        },
                        {
                            'trigger': 'enterHistroicalPrice',
                            'source': 'historicalCheck',
                            'dest': 'options',
                            'conditions': 'invalidCryptocurrency'
                        },
                        {
                            'trigger': 'goNewsOrGoBack',
                            'source': 'historicalPrice',
                            'dest': 'news',
                            'conditions': 'choosedNews'
                        },
                        {
                            'trigger': 'goNewsOrGoBack',
                            'source': 'historicalPrice',
                            'dest': 'options',
                            'conditions': 'choosedOptions'
                        },
                        {
                            'trigger': 'enterNews',
                            'source': 'newsCheck',
                            'dest': 'news'
                        },
                        {
                            'trigger': 'goBackOptions',
                            'source': 'news',
                            'dest': 'options'
                        }
                    ],
                    "initial": 'init',
                    "auto_transitions": False,
                }
            )

    def choosedLatest(self, replyToken, message):
        return message == "1"
    def choosedHistorical(self, replyToken, message):
        return message == "2"
    def choosedNews(self, replyToken, message):
        return message == "3"
    def choosedOptions(self, replyToken, message):
        return message == "0"

    def validCryptocurrency(self, replyToken, message):
        if len(message) > 5:
            return False
        result = client.query(generateQueryString(message, "latest"))
        if queryValidChecker(result):
            return True
        else:
            return False

    def invalidCryptocurrency(self, replyToken, message):
        if len(message) > 5:
            return True
        result = client.query(generateQueryString(message, "latest"))
        if queryValidChecker(result):
            return False
        else:
            return True

    def on_enter_options(self, replyToken, message):
        options_str = (
        "Welcome to use cryptocurrency price checker.\n" +
        "\n" +
        "[Latest] For the latest price, please enter 1.\n" +
        "[Historical] For historical price, please enter 2.\n" +
        "[News] For related news, please enter 3."
        )
        LineAPI.sendReplyMessage(replyToken, options_str)

    def on_enter_latestCheck(self, replyToken, message):
        prompt_str = (
                "Please enter the cryptocurrency you want to query.\n" +
                "For example, if you want to check Bitcoin, enter BTC.\n" +
                "If you want to check Ethereum, enter ETH.\n" +
                "If you entered invalid currency, you will be redirected back to options."
                )
        LineAPI.sendReplyMessage(replyToken, prompt_str)

    def on_enter_latestPrice(self, replyToken, message):
        result = client.query(generateQueryString(message, "latest"))
        price = priceParser(result)
        price = round(price, 2)
        returnString = (
                "The price of " + str(message) + " is " + str(price) + " USD now.\n\n" +
                "[News] If you want to check the news, enter 3.\n" +
                "[Options] If you want to go back to options, enter 0."
            )
        self.lastCheckCurrency = str(message)
        LineAPI.sendReplyMessage(replyToken, returnString)

    def on_enter_historicalCheck(self, replyToken, message):
        prompt_str = (
                "Please enter the cryptocurrency you want to query.\n" +
                "For example, if you want to check Bitcoin, enter BTC.\n" +
                "If you want to check Ethereum, enter ETH.\n" +
                "If you entered invalid currency, you will be redirected back to options."
            )
        LineAPI.sendReplyMessage(replyToken, prompt_str)

    def on_enter_historicalPrice(self, replyToken, message):
        latest = client.query(generateQueryString(message, "latest"))
        latestPrice = priceParser(latest)
        latestPrice = round(latestPrice, 2)
        historical = client.query(generateQueryString(message, "historical"))
        historicalPrice = priceParser(historical)
        historicalPrice = round(historicalPrice, 2)
        growthRate = round(float((latestPrice - historicalPrice) / historicalPrice), 4)
        returnString = (
                "The current price of " + str(message) + " is " + str(latestPrice) + " USD now.\n" +
                "The price 24 hours ago is " + str(historicalPrice) + " USD.\n" +
                "The growth rate is " + str(growthRate * 100) + "%.\n\n" +
                "[News] If you want to check the news, enter 3.\n" +
                "[Options] If you want to go back to options, enter 0."
            )
        self.lastCheckCurrency = str(message)
        LineAPI.sendReplyMessage(replyToken, returnString)

    def on_enter_newsCheck(self, replyToken, message):
        prompt_str = (
                "Please enter the keyword you want to search.\n"
            )
        LineAPI.sendReplyMessage(replyToken, prompt_str)

    def on_enter_news(self, replyToken, message):
        if message == '3':
            newsString = getNews(self.lastCheckCurrency)
        else:
            newsString = getNews(message)
        newsString = (
                "The news about " + self.lastCheckCurrency + ".\n\n" +
                newsString
            )
        LineAPI.sendReplyMessage(replyToken, newsString)
        self.goBackOptions(reply_token, message)
