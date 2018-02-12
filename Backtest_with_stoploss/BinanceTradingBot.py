# TradingBot class

import time
import requests
from datetime import datetime
import hmac, hashlib, base64

import sys

from TradingBot import TradingBot
from Utils import nonceGenerator
from Constants import *

try:
    #python2
    from urllib import urlencode
except ImportError:
    #python3
    from urllib.parse import urlencode


class BinanceTradingBot(TradingBot):
    def __init__(self, symbol, timeframe, idle_period, stoploss, limit, 
        rsi_range1, rsi_range2, start_time=None, end_time=None):
        super(BinanceTradingBot, self).__init__(symbol, 'binance', timeframe, idle_period, stoploss, limit,
            rsi_range1, rsi_range2, start_time, end_time)

        self.logger.error('Binance bot is disabled for now. Please use Bitfinex bot.')
        sys.exit(1)

    def __get_signature(self, payload_base64_encoded):
        """
        params: json encoded parameter
        """
        signature = hmac.new(key=str.encode(BINANCE_API_SECRET),
                             msg=payload_base64_encoded,
                             digestmod=hashlib.sha256).hexdigest()
        return signature

    def place_buy_limit_order(self, amount = 0.00, price = 0.00):
        # 
        ts = datetime.now()
        ts = time.mktime(ts.timetuple())
        ts = int(round(ts * 1000))
        # 
        payload_object = {
            'symbol': self.symbol,
            'side':'BUY',
            'type': 'LIMIT',
            'timeInForce': 'GTC',
            'quantity': str(amount),
            'price': str(price),
            'recvWindow':10000,
            'timestamp':ts
        }
        payload_text = urlencode(payload_object)
        payload_base64_encoded = base64.b64encode(str.encode(payload_text))

        payload_object.update({
            'signature': self.__get_signature(payload_base64_encoded)
        })

        headers = {
            'X-MBX-APIKEY':BINANCE_API_KEY
        }

        response = requests.post(
            url=API_BINANCE_ENDPOINT + API_BINANCE_ORDER, 
            data=urlencode(payload_object), 
            headers=headers
        )
        response_json = response.json()

        if 'orderId' not in response_json:
            self.logger.error("Failed to place [BUY] limit order: ["
                                + response_json["msg"] + "]")
            return {
                "successful": False
            }
        else:
            self.logger.info("Successfully placed [BUY] limit order: ["
                             + str(response_json) + "]")
            return {
                "successful": True,
                "order_id": response_json["orderId"]
            }

    def place_sell_limit_order(self, amount = 0.00, price = 0.00):
        # 
        ts = datetime.now()
        ts = time.mktime(ts.timetuple())
        ts = int(round(ts * 1000))
        # 
        payload_object = {
            'symbol': self.symbol,
            'side':'SELL',
            'type': 'LIMIT',    
            'timeInForce': 'GTC',            
            'quantity': str(amount),
            'price': str(price),
            'recvWindow':10000,
            'timestamp':ts
        }
        payload_text = urlencode(payload_object)
        payload_base64_encoded = base64.b64encode(str.encode(payload_text))

        payload_object.update({
            'signature': self.__get_signature(payload_base64_encoded)
        })

        headers = {
            'X-MBX-APIKEY':BINANCE_API_KEY
        }

        response = requests.post(
            url=API_BINANCE_ENDPOINT + API_BINANCE_ORDER, 
            data=urlencode(payload_object), 
            headers=headers
        )
        response_json = response.json()

        if 'orderId' not in response_json:
            self.logger.error("Failed to place [SELL] limit order: ["
                                + response_json["msg"] + "]")
            return {
                "successful": False
            }
        else:
            self.logger.info("Successfully placed [SELL] limit order: ["
                             + str(response_json) + "]")
            return {
                "successful": True,
                "order_id": response_json["orderId"]
            }
