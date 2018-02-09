# TradingBot class

import requests
import hmac, hashlib, base64
import json

from TradingBot import TradingBot
from Utils import nonceGenerator
from Constants import *


class BitfinexTradingBot(TradingBot):
    def __init__(self, symbol, timeframe, idle_period, stoploss, limit,
        rsi_range1, rsi_range2, MACD_trend_qty, MACD_flat_qty, MACD_flat_range, RSI_trend_qty, start_time=None, end_time=None):
        super(BitfinexTradingBot, self).__init__(symbol, 'bitfinex', timeframe, idle_period, stoploss, limit,
            rsi_range1, rsi_range2, MACD_trend_qty, MACD_flat_qty, MACD_flat_range, RSI_trend_qty, start_time, end_time)

    def __get_signature(self, payload_base64_encoded):
        """
        params: json encoded parameter
        """
        signature = hmac.new(key=str.encode(BITFINEX_API_SECRET),
                             msg=payload_base64_encoded,
                             digestmod=hashlib.sha384).hexdigest()
        return signature

    def place_buy_limit_order(self, amount = 0.00, price = 0.00):
        #
        payload_object = {
            'request': API_BITFINEX_ORDER,
            'nonce': nonceGenerator.getNonce(),
            'symbol': self.symbol,
            'amount': str(amount),
            'price': str(price),
            'exchange': 'bitfinex',
            'side': 'buy',
            'type': 'exchange limit'
        }
        payload_text = json.dumps(payload_object)
        payload_base64_encoded = base64.b64encode(str.encode(payload_text))
        headers = {
            'X-BFX-APIKEY': BITFINEX_API_KEY,
            'X-BFX-PAYLOAD': payload_base64_encoded,
            'X-BFX-SIGNATURE': self.__get_signature(payload_base64_encoded)
        }

        response = requests.post(
            url=API_BITFINEX_ENDPOINT + API_BITFINEX_ORDER,
            data={},
            headers=headers
        )
        response_json = response.json()

        if 'order_id' not in response_json:
            self.logger.error("Failed to place [BUY] limit order: ["
                                + response_json["message"] + "]")
            return {
                "successful": False
            }
        else:
            self.logger.info("Successfully placed [BUY] limit order: ["
                             + str(response_json) + "]")
            return {
                "successful": True,
                "order_id": response_json["order_id"]
            }

    def place_sell_limit_order(self, amount = 0.00, price = 0.00):
        #
        payload_object = {
            'request': API_BITFINEX_ORDER,
            'nonce': nonceGenerator.getNonce(),
            'symbol': self.symbol,
            'amount': str(amount),
            'price': str(price),
            'exchange': 'bitfinex',
            'side': 'sell',
            'type': 'exchange limit'
        }
        payload_text = json.dumps(payload_object)
        payload_base64_encoded = base64.b64encode(str.encode(payload_text))
        headers = {
            'X-BFX-APIKEY': BITFINEX_API_KEY,
            'X-BFX-PAYLOAD': payload_base64_encoded,
            'X-BFX-SIGNATURE': self.__get_signature(payload_base64_encoded)
        }

        response = requests.post(
            url=API_BITFINEX_ENDPOINT + API_BITFINEX_ORDER,
            data={},
            headers=headers
        )
        response_json = response.json()

        if 'order_id' not in response_json:
            self.logger.error("Failed to place [SELL] limit order: ["
                                + response_json["message"] + "]")
            return {
                "successful": False
            }
        else:
            self.logger.info("Successfully placed [SELL] limit order: ["
                             + str(response_json) + "]")
            return {
                "successful": True,
                "order_id": response_json["order_id"]
            }
