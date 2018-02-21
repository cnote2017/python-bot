import logging
import random
import traceback
import requests
import hmac, hashlib, base64
import json

import time

import Constants
from Utils import nonceGenerator, no_exp_str
from Constants import *


class ExchangeResponse:
    def __init__(self, success, order_id: int=None, message: str=None, json: dict=None, **kwargs):
        self.success = success
        self.order_id = order_id
        self.message = message
        self.kwargs = kwargs
        self.json = json


class BaseAPI:
    def __init__(self, bot):
        self.bot = bot
        self.logger = logging.getLogger('main_log')

    def place_limit_order(self, side, amount=0.00, price=0.00) -> ExchangeResponse:
        pass

    def get_order_status(self, order_id) -> ExchangeResponse:
        pass

    def cancel_order(self, order_id) -> ExchangeResponse:
        pass


class BitfinexAPIHandler(BaseAPI):
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

    def place_limit_order(self, side, amount=0.00, price=0.00) -> ExchangeResponse:
        side = side.lower()
        assert (side in ("buy", "sell"))
        #
        payload = {'request': API_BITFINEX_NEW_ORDER,
                   'nonce': nonceGenerator.getNonce(),
                   'symbol': self.bot.symbol,
                   'amount': no_exp_str(amount),
                   'price': no_exp_str(price),
                   'exchange': 'bitfinex',
                   'type': 'exchange limit',
                   'side': side}

        headers = self.process_payload(payload)

        try:
            response = requests.post(
                url=API_BITFINEX_ENDPOINT + API_BITFINEX_NEW_ORDER,
                data={},
                headers=headers,
                timeout=REQUEST_TIMEOUT
            )
            response_json = response.json()
        except:
            self.logger.error("Exception during handling exchange response.", exc_info=True)
            return ExchangeResponse(False, exception=traceback.format_exc())

        if 'order_id' not in response_json:
            self.bot.logger.error("Failed to place [%s] limit order: [%s]"
                              % (payload['side'], str(response_json["message"])))
            return ExchangeResponse(False, message=str(response_json["message"]))

        else:
            order_id = response_json["order_id"]
            self.bot.logger.info("Successfully placed limit order: {} {} {} @ {}. Order ID {}:".format(
                side, amount, self.bot.symbol, price, order_id))

            return ExchangeResponse(True, order_id=order_id, json=response_json)

    def place_market_order(self, side, amount=0.00) -> ExchangeResponse:

        side = side.lower()
        assert (side in ("buy", "sell"))
        payload = {'request': API_BITFINEX_NEW_ORDER,
                   'nonce': nonceGenerator.getNonce(),
                   'symbol': self.bot.symbol,
                   'amount': no_exp_str(amount),
                   'price': no_exp_str(random.random()),
                   'exchange': 'bitfinex',
                   'type': 'exchange market',
                   'side': side}

        headers = self.process_payload(payload)

        try:
            response = requests.post(
                url=API_BITFINEX_ENDPOINT + API_BITFINEX_NEW_ORDER,
                data={},
                headers=headers,
                timeout=REQUEST_TIMEOUT
            )
            response_json = response.json()
        except:
            self.logger.error("Exception during handling exchange response.", exc_info=True)
            return ExchangeResponse(False, exception=traceback.format_exc())

        if 'order_id' not in response_json:
            self.bot.logger.error("Failed to place [%s] market order: [%s]"
                              % (payload['side'], str(response_json["message"])))
            return ExchangeResponse(False, message=str(response_json["message"]))

        else:
            order_id = response_json["order_id"]
            self.bot.logger.info("Successfully placed market order: {} {} {}. Order ID {}:".format(
                side, amount, self.bot.symbol, order_id))

            return ExchangeResponse(True, order_id=order_id, json=response_json)

    def place_stop_order(self, amount: float, stop_value: float=None) -> ExchangeResponse:

        payload = {'request': API_BITFINEX_NEW_ORDER,
                   'nonce': nonceGenerator.getNonce(),
                   'symbol': self.bot.symbol,
                   'amount': no_exp_str(amount),
                   'price': no_exp_str(stop_value),
                   'exchange': 'bitfinex',
                   'type': 'exchange stop',
                   'side': "sell",
                   }

        headers = self.process_payload(payload)

        try:
            response = requests.post(
                url=API_BITFINEX_ENDPOINT + API_BITFINEX_NEW_ORDER,
                data={},
                headers=headers,
                timeout=REQUEST_TIMEOUT
            )
            response_json = response.json()
        except:
            self.logger.error("Exception during handling exchange response.", exc_info=True)
            return ExchangeResponse(False, exception=traceback.format_exc())

        if 'order_id' not in response_json:
            self.bot.logger.error("Failed to place stop order: [%s]" % (str(response_json["message"])))
            return ExchangeResponse(False, message=str(response_json["message"]))
        else:
            order_id = response_json["order_id"]
            self.bot.logger.info(f"Successfully placed stop order")
            return ExchangeResponse(True, order_id=order_id, json=response_json)

    def get_order_status(self, order_id) -> ExchangeResponse:
        """ Get the order status from the exchange"""
        payload = {
            "request": API_BITFINEX_ORDER_STATUS,
            "nonce": nonceGenerator.getNonce(),
            "order_id": order_id
        }

        headers = self.process_payload(payload)
        try:
            response = requests.post(
                url=API_BITFINEX_ENDPOINT + API_BITFINEX_ORDER_STATUS,
                data={},
                headers=headers,
                timeout=REQUEST_TIMEOUT
            )
            response_json = response.json()
        except:
            self.logger.error("Exception during handling exchange response.", exc_info=True)
            return ExchangeResponse(False, exception=traceback.format_exc())

        if "is_live" not in response_json:
            self.bot.logger.error("Failed to get order status for order ID {} . Message: {}".format(
                order_id, response_json["message"]))
            return ExchangeResponse(False, message=str(response_json["message"]))
        else:
            return ExchangeResponse(True, json=response_json)

    def cancel_order(self, order_id) -> ExchangeResponse:
        payload = {
            "request": API_BITFINEX_CANCEL_ORDER,
            "nonce": nonceGenerator.getNonce(),
            "order_id": order_id
        }

        headers = self.process_payload(payload)
        try:
            response = requests.post(
                url=API_BITFINEX_ENDPOINT + API_BITFINEX_CANCEL_ORDER,
                data={},
                headers=headers,
                timeout=REQUEST_TIMEOUT
            )
            response_json = response.json()
        except:
            self.logger.error("Exception during handling exchange response.", exc_info=True)
            return ExchangeResponse(False, exception=traceback.format_exc())

        for _ in range(5):
            status = self.get_order_status(order_id)
            if not status.success or status.json.get("is_cancelled", False):
                time.sleep(5)
            else:
                self.bot.logger.info("Cancelled order: {}".format(order_id))
                return ExchangeResponse(True, order_id=order_id, json=response_json)

        if "is_cancelled" not in response_json:
            self.bot.logger.error("Failed to get order status for order ID {} . Message: {}".format(
                order_id, response_json["message"]))
        elif not response_json["is_cancelled"]:
            self.bot.logger.error("Order not cancelled. Order ID {} . Json: {}".format(
                order_id, str(response_json)))

        return ExchangeResponse(False, order_id=order_id, json=response_json)

    def get_active_orders(self) -> ExchangeResponse:
        payload = {
            "request": API_BITFINEX_ACTIVE_ORDERS,
            "nonce": nonceGenerator.getNonce(),
        }

        headers = self.process_payload(payload)
        try:
            response = requests.post(
                url=API_BITFINEX_ENDPOINT + API_BITFINEX_ACTIVE_ORDERS,
                data={},
                headers=headers,
                timeout=REQUEST_TIMEOUT
            )
            response_json = response.json()
        except:
            self.logger.error("Exception during handling exchange response.", exc_info=True)
            return ExchangeResponse(False, exception=traceback.format_exc())

        return ExchangeResponse(True, json=response_json)

    def get_active_positions(self) -> ExchangeResponse:
        payload = {
            "request": API_BITFINEX_ACTIVE_POSITIONS,
            "nonce": nonceGenerator.getNonce(),
        }

        headers = self.process_payload(payload)
        try:
            response = requests.post(
                url=API_BITFINEX_ENDPOINT + API_BITFINEX_ACTIVE_POSITIONS,
                data={},
                headers=headers,
                timeout=REQUEST_TIMEOUT
            )
            response_json = response.json()
        except:
            self.logger.error("Exception during handling exchange response.", exc_info=True)
            return ExchangeResponse(False, exception=traceback.format_exc())

        return ExchangeResponse(True, json=response_json)

    def get_balances(self) -> ExchangeResponse:
        payload = {
            "request": API_BITFINEX_BALANCES,
            "nonce": nonceGenerator.getNonce(),
        }

        headers = self.process_payload(payload)
        print(API_BITFINEX_ENDPOINT + API_BITFINEX_BALANCES)
        try:
            response = requests.post(
                url=API_BITFINEX_ENDPOINT + API_BITFINEX_BALANCES,
                data={},
                headers=headers,
                timeout=REQUEST_TIMEOUT
            )
            response_json = response.json()
        except:
            self.logger.error("Exception during handling exchange response.", exc_info=True)
            return ExchangeResponse(False, exception=traceback.format_exc())

        return ExchangeResponse(True, json=response_json)

    def get_key_info(self) -> ExchangeResponse:
        payload = {
            "request": API_BITFINEX_KEY_INFO,
            "nonce": nonceGenerator.getNonce(),
        }

        headers = self.process_payload(payload)
        try:
            response = requests.post(
                url=API_BITFINEX_ENDPOINT + API_BITFINEX_KEY_INFO,
                data={},
                headers=headers,
                timeout=REQUEST_TIMEOUT
            )
            response_json = response.json()
        except:
            self.logger.error("Exception during handling exchange response.", exc_info=True)
            return ExchangeResponse(False, exception=traceback.format_exc())

        return ExchangeResponse(True, json=response_json)

