import datetime
import enum
import sys

from BitfinexAPI import BitfinexAPIHandler


class Side(enum.Enum):
    long = enum.auto()
    short = enum.auto()


@enum.unique
class OrderState(enum.Enum):
    """ The state that the order is currently in. All order states are mutually exclusive."""

    created = enum.auto()
    rejected = enum.auto()
    placed = enum.auto()
    filled = enum.auto()
    canceled = enum.auto()
    closed = enum.auto()

    # partially_filled = enum.auto()

    def __repr__(self):
        return '<%s.%s>' % (self.__class__.__name__, self.name)


class Order:
    def __init__(self, is_long: bool, size: int, limit_price: float,
                 order_manager, exchange_id: int=None):
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
        self.exchange_id = exchange_id
        self.order_manager = order_manager

        self.state = OrderState.created
        self.submit_time = datetime.datetime.now()

    def update_status(self):
        if self.state is not OrderState.placed:
            return

        status = self.order_manager.api.get_order_status(self.exchange_id)
        if float(status["executed_amount"]) > 0:
            self.state = OrderState.filled
            self.order_manager.bot.logger.info('Order {} filled'.format(self.exchange_id))

    def liquidate(self):
        self.cancel()
        self.close_position()

    def cancel(self):
        if self.state == OrderState.placed:
            result = self.order_manager.api.cancel_order(self.exchange_id)
            if result is True:
                self.state = OrderState.canceled
            # self.order_manager.bot.logger.info('Cancelling order {}'.format(self.exchange_id))

    def close_position(self):
        if self.state == OrderState.filled:
            self.state = OrderState.closed

            limit_price = self.order_manager.bot.get_current_price()
            new_order = Order(not self.is_long, self.size, limit_price, self.order_manager)
            self.order_manager.bot.logger.info('Closing order {}'.format(self.exchange_id))
            self.order_manager.place_order(new_order)


class OrderManager:
    """ A manager class for orders.

     All orders operations called by trading bots should use this class."""

    def __init__(self, bot):
        self.bot = bot
        self.orders = []
        self.positions = []
        self.direction = None
        self.api = BitfinexAPIHandler(bot)
        self.max_orders = bot.max_orders

    def handle_trade_signal(self, signal: str):
        """
        Processes a string trade signal in order to generate trades.

        Allowed signal values are: "OPENBUY", "OPENSELL", "CLOSEBUY", "CLOSESELL", "CLOSEBUY/SELL".
        If there are positions open on one side (for example, long) receiving a signal of the opposite
        side (for example, "OPENSELL") will close *all* orders and positions that are currently open.

        :type signal: str
        """

        allowed_signals = ["OPENBUY", "OPENSELL", "CLOSEBUY", "CLOSESELL", "CLOSEBUY/SELL"]

        if signal not in allowed_signals:
            self.bot.logger.error("Received unknown trade signal: {}".format(signal))
            sys.exit(1)

        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if signal == "OPENSELL":
            if self.direction is Side.long:
                self.close_all()
                self.direction = None

            self.bot.logger.info('Received OPENSELL signal but short selling is disabled. Continuing to wait for long signal.')
            return
            # self.direction = Side.short
            # size = self.bot.order_size
            # limit_price = self.bot.get_current_price()
            # order = Order(False, size, limit_price, self)
            # self.place_order(order)
            # self.bot.logger.info('Placed %s ORDER... Timestamp: %s | Last Price: %s | ID: %d',
            #                  signal, timestamp, limit_price, str(order.exchange_id))

        if signal == "OPENBUY":
            if self.direction is Side.short:
                self.close_all()

            self.direction = Side.long
            size = self.bot.order_size
            limit_price = self.bot.get_current_price()
            order = Order(True, size, limit_price, self)
            # self.bot.logger.info('Placing %s ORDER... Timestamp: %s | Last Price: %s | ID: %d',
            #                      signal, timestamp, limit_price, str(order.exchange_id))
            self.place_order(order)

        if signal in ["CLOSEBUY", "CLOSESELL", "CLOSEBUY/SELL"]:
            self.bot.logger.info('Received {} signal. Closing all positions.'.format(signal))
            self.direction = None
            self.close_all()

    def check_order_limit(self):
        if self.max_orders is None or len(self.orders) < self.max_orders:
            return True
        else:
            self.bot.logger.error("Reached the maximum number of orders. Exiting.")
            sys.exit(1)

    def place_order(self, order: Order):
        """ Attempt to place the order on the exchange. """

        self.check_order_limit()
        side = "buy" if order.is_long else "sell"
        response = self.api.place_limit_order(side, order.size, order.limit_price)

        if response['successful']:
            order.exchange_id = response['order_id']
            order.state = OrderState.placed
        else:
            order.state = OrderState.rejected

        self.orders.append(order)

    def close_all(self):
        for order in self.orders:
            order.update_status()
            order.liquidate()

    def update_orders(self):
        for order in self.orders:
            order.update_status()
