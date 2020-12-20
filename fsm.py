from transitions.extensions import GraphMachine

from utils import send_text_message


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
                            'conditions': 'goNews'
                        },
                        {
                            'trigger': 'goNewsorGoBack',
                            'source': 'latestPrice',
                            'dest': 'options',
                            'conditions': 'goBackOptions',
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
                            'conditions': 'goNews'
                        },
                        {
                            'trigger': 'goNewsOrGoBack',
                            'source': 'historicalPrice',
                            'dest': 'options',
                            'conditions': 'goBackOptions'
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
