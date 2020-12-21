from transitions.extensions import GraphMachine

from utils import generateQueryString, queryValidChecker, priceParser

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
                            'trigger': 'goNewsorGoBack',
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
                            'dest': 'news',
                            'conditions': 'validCryptocurrency'
                        },
                        {
                            'trigger': 'enterNews',
                            'source': 'newsCheck',
                            'dest': 'options',
                            'conditions': 'invalidCryptocurrency'
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
        return text == "1"
    def choosedHistorical(self, replyToken, message):
        return text == "2"
    def choosedNews(self, replyToken, message):
        return text == "3"
    def choosedOptions(self, replyToken, message):
        return text == "0"

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
        LineAPI.sendReplyMessage(replyToken, "You entered invalid cryptocurrency!")
        if queryValidChecker(result):
            return False
        else:
            return True

    def on_enter_options(self, replyToken, message):
        options_str = """
        Welcome to use cryptocurrency price checker.

        [Latest] For the latest price, please enter 1.
        [Historical] For historical price, please enter 2.
        [News] For related news, please enter 3.
        """
        LineAPI.sendReplyMessage(replyToken, options_str)

    def on_enter_latestCheck(self, replyToken, message):
        prompt_str = """
        Please enter the cryptocurrency you want to query.
        For example, if you want to check Bitcoin, enter BTC.
        If you want to check Ethereum, enter ETH.
        """
        LineAPI.sendReplyMessage(replyToken, message)

    def on_enter_latestPrice(self, replyToken, message):
        result = client.query(generateQueryString(message, "latest"))
        price = priceParser(result)
        returnString = "The price of " + str(message) + " is " + str(price) + " USD now."
        self.lastCheckCurrency = str(message)
        LineAPI.sendReplyMessage(replyToken, returnString)
        returnString = """
        [News] If you want to check the news, enter 3
        [Options] If you want to go back to options, enter 0
        """
        LineAPI.sendReplyMessage(replyToken, returnString)
