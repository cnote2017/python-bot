import datetime
import enum
import itertools
import logging
import sys

from BitfinexAPI import BitfinexAPIHandler
from Constants import REQUEST_RETRY_INTERVAL


class Side(enum.Enum):
    long = enum.auto()
    short = enum.auto()


class OrderType(enum.Enum):
    limit = enum.auto()
    stop = enum.auto()
    market = enum.auto()


class OCOType(enum.Enum):
    take_profit = enum.auto()
    stop_loss = enum.auto()


@enum.unique
class OrderState(enum.Enum):
    """ The state that the order is currently in. All order states are mutually exclusive."""

    created = enum.auto()
    rejected = enum.auto()
    placed = enum.auto()
    filled = enum.auto()
    canceled = enum.auto()
    closed = enum.auto()
    partially_filled = enum.auto()

    def __repr__(self):
        return '<%s.%s>' % (self.__class__.__name__, self.name)


class Order:
    id_gen = itertools.count()

    def __init__(self, is_long: bool, size: float, limit_price: float,
                 order_manager, exchange_id: int = None, forbid_liquidation=False,
                 order_type=OrderType.limit, take_profit: float = None, stop_loss: float = None):
        """
        :param is_long:
        :param size:
        :param limit_price:
        :param exchange_id:
        :param order_manager:
        """

        assert type(is_long) is bool

        self.is_long = is_long
        self.size = size
        self.limit_price = limit_price
        self.exchange_id = -next(Order.id_gen)
        self.order_manager = order_manager
        self.forbid_liquidation = forbid_liquidation

        self.state = OrderState.created
        self.submit_time = datetime.datetime.now()
        self.order_type = order_type
        self.stop_loss = stop_loss
        self.take_profit = take_profit
        self.linked_order = None
        self.OCO_type = None
        self.source_order = None
        self.logger = logging.getLogger('main_log')
        self.amount_filled = 0

    def update_status(self):
        if self.state not in [OrderState.placed, OrderState.partially_filled] :
            return

        status = self.order_manager.api.get_order_status(self.exchange_id)
        if status.success:
            amount = float(status.json["executed_amount"])
            if amount > 0:
                self.amount_filled = amount
                if amount >= self.size * 0.9999:
                    self.state = OrderState.filled
                    self.logger.info('Order {} filled'.format(self.exchange_id))
                    self.amount_filled = amount
                    self.on_fill()
                    if not self.is_long:
                        self.state = OrderState.closed
                else:
                    self.state = OrderState.partially_filled
                    if self.amount_filled < amount:
                        self.logger.info(f'Order {self.exchange_id} partially filled. Amount: {amount} / {self.size}')
                    self.amount_filled = amount
                    self.on_fill()

    def liquidate(self):
        if self.forbid_liquidation:
            return

        if self.state not in (OrderState.placed, OrderState.filled):
            return

        self.logger.info(f"Liquidating order {self.exchange_id} ({self.order_type.name})")

        for _ in range(10):
            self.update_status()
            if self.state == OrderState.placed:
                self.cancel(retries=1)
            elif self.state in [OrderState.filled, OrderState.partially_filled]:
                self.close_position(retries=1)
            else:
                break

        if self.state in (OrderState.placed, OrderState.filled):
            self.logger.info(f"Liquidating order {self.exchange_id} failed.")

    def cancel(self, retries=5):
        self.logger.info(f"Canceling order {self.exchange_id}, type {self.order_type}")

        for _ in range(retries):
            result = self.order_manager.api.cancel_order(self.exchange_id)
            if result.success:
                self.state = OrderState.canceled
                self.logger.info("Canceled order {}".format(self.exchange_id))
                break

            self.logger.error("Failed to cancel order {}. Will try again in {}" \
                              .format(self.exchange_id, REQUEST_RETRY_INTERVAL))

    def close_position(self, retries=10):
        self.logger.info("Closing position. Order id {}"
                         .format(self.exchange_id))
        for _ in range(retries):
            self.logger.info('Closing order {}'.format(self.exchange_id))
            success = self.order_manager.place_order(not self.is_long, self.amount_filled, None,
                                                     forbid_liquidation=True, is_market=True)
            if success:
                self.state = OrderState.closed
                self.cancel(10)
                self.logger.info(f'Successfully created an exit for buy order {self.exchange_id}')
                break

            self.logger.error("Failed to create an exit for buy order {}. Will try again in {}" \
                              .format(self.exchange_id, REQUEST_RETRY_INTERVAL))

    def on_fill(self):
        self.order_manager.get_current_balance()

        if self.state is not OrderState.filled:
            return

        if self.is_long:
            self.make_stop_order(source=self)

        if self.order_type == OrderType.stop:
            self.logger.info(f"Stop triggered (id: {self.exchange_id}) for order {self.source_order.exchange_id}.")

            self.source_order.state = OrderState.closed


    def make_stop_order(self, source, retries=10):
        self.logger.info(f"Placing stops for order {self.exchange_id}")
        for _ in range(retries):
            size = self.size if self.state is OrderState.filled else self.amount_filled
            success = self.order_manager.place_stop_order(size, source_order=source)
            if success:
                self.logger.info(f'Successfully created stop')
                break

            self.logger.error(f"Failed to create stops. Will try again in {REQUEST_RETRY_INTERVAL}")


class OrderManager:
    """ A manager class for orders.

     All orders operations called by trading bots should use this class."""

    def __init__(self, bot):
        self.bot = bot

        self.orders = []
        self.positions = []
        self.direction = None
        self.max_orders = bot.max_orders
        self.api = BitfinexAPIHandler(bot)
        self.logger = logging.getLogger('main_log')

    def get_current_balance(self):
        balances = self.api.get_balances()
        balance = None
        if balances.success:
            sym_balances = [b for b in balances.json
                           if b['currency'] == self.bot.symbol.lower()[:3]
                           and type == 'exchange']

            if len(sym_balances):
                balance = sym_balances[0]

        amount, available = None, None
        resp = self.api.get_active_positions()
        if resp.success:
            self.logger.info("Active positions:" + resp.json)

        if balance is not None:
            amount = balance['amount']
            available = balance['available']
            self.logger.info(
                f"Current balances: amount = {amount}, available = {available}")
        else:
            self.logger.info("No exchange balance info available for the current symbol")

        return available

    def handle_trade_signal(self, signal: str):
        """
        Processes a string trade signal in order to generate trades.

        Allowed signal values are: "OPENBUY", "OPENSELL", "CLOSEBUY", "CLOSESELL", "CLOSEBUY/SELL".
        If there are positions open on one side (for example, long) receiving a signal of the opposite
        side (for example, "OPENSELL") will close *all* orders and positions that are currently open.

        :type signal: str
        """

        allowed_signals = ["OPENBUY", "OPENSELL", "CLOSEBUY", "CLOSESELL", "CLOSEBUY/SELL"]

        if not signal:
            self.logger.info('No signal to trade.')
            return

        if signal not in allowed_signals:
            self.logger.error("Received unknown trade signal: {}".format(signal))
            sys.exit(1)

        self.bot.logger.info("Received signal: {}".format(signal))
        if signal == "OPENBUY":
            self.cancel_old_buy_orders()
            self.direction = Side.long
            size = self.bot.order_size
            limit_price = self.bot.get_current_price()
            self.place_order(True, size, limit_price)

        if signal in ["CLOSEBUY", "CLOSESELL", "CLOSEBUY/SELL", "OPENSELL"]:
            self.bot.logger.info('Received {} signal. Closing all positions.'.format(signal))
            self.direction = None
            self.close_all()

        self.bot.logger.info('Finished processing the signal.')

    def check_order_limit(self):
        if self.max_orders is None or len([o for o in self.orders if o.is_long]) < self.max_orders:
            return True
        else:
            self.logger.error("Reached the maximum number of orders. Exiting.")
            sys.exit(1)

    def place_order(self, is_long, size, limit_price, retries=10, forbid_liquidation=False,
                    is_market: bool = False):
        """ Attempt to place the order on the exchange. """
        self.check_order_limit()

        for _ in range(retries):
            if is_market:
                order, response = self.place_market_order(is_long, size, forbid_liquidation)
                order.order_type = OrderType.market
            else:
                order, response = self.place_limit_order(is_long, size, limit_price, forbid_liquidation)

            self.orders.append(order)
            if response.success:
                order.exchange_id = response.order_id
                if not is_market:
                    order.state = OrderState.placed
                    self.logger.info("Limit order accepted. Id: {}".format(order.exchange_id))
                else:
                    order.state = OrderState.closed
                    self.logger.info("Market order accepted. Id: {}".format(order.exchange_id))
                return True
            else:
                order.state = OrderState.rejected
                self.logger.error(
                    f"Order rejected. Will try again in {REQUEST_RETRY_INTERVAL}")

        return False

    def place_market_order(self, is_long, size, forbid_liquidation):
        side = "buy" if is_long else "sell"
        self.logger.info("Placing {} market order: {} {}".format(side, size, self.bot.symbol))
        order = Order(is_long, size, None, self, forbid_liquidation=forbid_liquidation)
        response = self.api.place_market_order(side, order.size)
        return order, response

    def place_limit_order(self, is_long, size, limit_price, forbid_liquidation):
        side = "buy" if is_long else "sell"
        self.logger.info("Placing {} limit order: {} {} @ {}"
                         .format(side, size, self.bot.symbol, limit_price))
        order = Order(is_long, size, limit_price, self, forbid_liquidation=forbid_liquidation)
        response = self.api.place_limit_order(side, order.size, order.limit_price)
        return order, response

    def place_stop_order(self, size: float, source_order):
        stop_loss = self.bot.calc_stop_loss()
        self.logger.info(f"Placing stop order: {stop_loss}")
        order = Order(False, size, stop_loss, order_manager=self, order_type=OrderType.stop)

        response = self.api.place_stop_order(size, stop_value=stop_loss)
        if response.success:
            order.exchange_id = response.order_id
            order.state = OrderState.placed
            order.source_order = source_order
            self.logger.info(f"Stop order accepted. Id: {order.exchange_id}")
            self.orders.extend([order])
            return True
        else:
            self.logger.info(f"Stop order rejected.")
            return False

    def cancel_old_buy_orders(self):
        self.logger.info("Got a new buy signal. Canceling old ones.")
        for order in self.orders:
            if order.is_long and order.state == OrderState.placed:
                order.cancel()

    def close_all(self):
        # handle cancels first
        to_cancel = [o for o in self.orders
                     if o.state in [OrderState.placed, OrderState.partially_filled]]
        for order in to_cancel:
            order.liquidate()

        for order in self.orders:
            order.liquidate()

    def update_orders(self):
        for order in self.orders:
            order.update_status()

    def show_status(self):
        self.logger.info(f"====== Order status: {len(self.orders)} processed so far.======")
        if not len(self.orders):
            return

        for state in list(OrderState):
            orders = list(filter(lambda x: x.state == state, self.orders))
            if not len(orders):
                continue

            self.logger.info(f'Orders {state.name}: {len(orders)} total.')
            limit_orders = [o.exchange_id for o in orders if o.order_type == OrderType.limit]
            market_orders = [o.exchange_id for o in orders if o.order_type == OrderType.market]
            stop_orders = [o.exchange_id for o in orders if o.order_type == OrderType.stop]

            if len(limit_orders):
                self.logger.info(f'{state.name} limit order ids: {limit_orders}')
            if len(market_orders):
                self.logger.info(f'{state.name} market order ids: {market_orders}')
            if len(stop_orders):
                self.logger.info(f'{state.name} stop order ids: {stop_orders}')

        self.get_current_balance()
        self.logger.info("=" * 46)
