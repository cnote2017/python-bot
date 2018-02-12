
import requests
import hmac, hashlib, base64
import json

import time

import Constants
from Utils import nonceGenerator
from Constants import *


class BitfinexAPIHandler:
    def __init__(self, bot):
        self.bot = bot

    def __get_signature(self, payload_base64_encoded):
        """
        params: json encoded parameter
        """
        signature = hmac.new(key=str.encode(Constants.BITFINEX_API_SECRET),
                             msg=payload_base64_encoded,
                             digestmod=hashlib.sha384).hexdigest()
        return signature

    def process_payload(self, payload):
        payload_text = json.dumps(payload)
        payload_base64_encoded = base64.b64encode(str.encode(payload_text))
        headers = {
            'X-BFX-APIKEY': Constants.BITFINEX_API_KEY,
            'X-BFX-PAYLOAD': payload_base64_encoded,
            'X-BFX-SIGNATURE': self.__get_signature(payload_base64_encoded)
        }

        return headers

    def place_limit_order(self, side, amount=0.00, price=0.00):
        side = side.lower()
        assert (side in ("buy", "sell"))
        #
        payload = {'request': API_BITFINEX_NEW_ORDER,
                   'nonce': nonceGenerator.getNonce(),
                   'symbol': self.bot.symbol,
                   'amount': str(amount),
                   'price': str(price),
                   'exchange': 'bitfinex',
                   'type': 'exchange limit',
                   'side': side}

        headers = self.process_payload(payload)
        response = requests.post(
            url=API_BITFINEX_ENDPOINT + API_BITFINEX_NEW_ORDER,
            data={},
            headers=headers
        )
        response_json = response.json()

        if 'order_id' not in response_json:
            self.bot.logger.error("Failed to place [%s] limit order: [%s]"
                              % (payload['side'], str(response_json["message"])))
            return {
                "successful": False
            }
        else:
            order_id = response_json["order_id"]
            self.bot.logger.info("Successfully placed limit order: {} {} {} @ {}. Order ID {}:".format(
                side, amount, self.bot.symbol, price, order_id))

            return {
                "successful": True,
                "order_id": order_id
            }

    def get_order_status(self, order_id):
        """ Get the order status from the exchange"""
        payload = {
            "request": API_BITFINEX_ORDER_STATUS,
            "nonce": nonceGenerator.getNonce(),
            "order_id": order_id
        }

        headers = self.process_payload(payload)

        response = requests.post(
            url=API_BITFINEX_ENDPOINT + API_BITFINEX_ORDER_STATUS,
            data={},
            headers=headers
        )

        response_json = response.json()

        if "is_live" not in response_json:
            self.bot.logger.error("Failed to get order status for order ID {} . Message: {}".format(
                order_id, response_json["message"]))
        else:
            return response_json

    def cancel_order(self, order_id):
        payload = {
            "request": API_BITFINEX_CANCEL_ORDER,
            "nonce": nonceGenerator.getNonce(),
            "order_id": order_id
        }

        headers = self.process_payload(payload)
        response = requests.post(
            url=API_BITFINEX_ENDPOINT + API_BITFINEX_CANCEL_ORDER,
            data={},
            headers=headers
        )

        response_json = response.json()

        for _ in range(5):
            status = self.get_order_status(order_id)
            if not status.get("is_cancelled", False):
                time.sleep(1)
            else:
                self.bot.logger.info("Cancelled order: {}".format(order_id))
                return True

        if "is_cancelled" not in response_json:
            self.bot.logger.error("Failed to get order status for order ID {} . Message: {}".format(
                order_id, response_json["message"]))
        elif not response_json["is_cancelled"]:
            self.bot.logger.error("Order not cancelled. Order ID {} . Json: {}".format(
                order_id, str(response_json)))
        else:
            return True
