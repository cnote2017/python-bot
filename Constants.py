

BITFINEX_API_KEY = ''
BITFINEX_API_SECRET = ''


# Binance
BINANCE_API_KEY = '<Paste you API Key here>'
BINANCE_API_SECRET = '<Paste you API Secret here>'


# API constants
# Bitfinex
API_BITFINEX_ENDPOINT='https://api.bitfinex.com'
API_BITFINEX_TICKER='/v1/pubticker/'
API_BITFINEX_CANDLES='/v2/candles/'
API_BITFINEX_NEW_ORDER = '/v1/order/new'
API_BITFINEX_SYMBOL_DETAILS = API_BITFINEX_ENDPOINT + '/v1/symbols_details'
API_BITFINEX_ORDER_STATUS = '/v1/order/status'
API_BITFINEX_CANCEL_ORDER = "/v1/order/cancel"
API_BITFINEX_ACTIVE_ORDERS = '/v1/orders'
API_BITFINEX_ACTIVE_POSITIONS = '/v1/positions'
API_BITFINEX_BALANCES = '/v1/balances'
API_BITFINEX_KEY_INFO = '/v1/key_info'

# Binance
API_BINANCE_ENDPOINT='https://www.binance.com'
API_BINANCE_TICKER='/api/v1/ticker/allPrices'
API_BINANCE_CANDLES='/api/v1/klines'
API_BINANCE_ORDER = '/api/v3/order'

# API Time Intervals mapping
bitfinex_tf = {
    '1d': { 'interval': '1D', 'factor': 1 },
}
binance_tf = {
    '3h': { 'interval': '1h', 'factor': 3 },
}

ORDER_UPDATE_INTERVAL = 5
TICKER_UPDATE_INTERVAL = 5
REQUEST_RETRY_INTERVAL = 20
REQUEST_TIMEOUT = 30
