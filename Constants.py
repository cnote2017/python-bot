
# API credentials
# Bitfinex
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
API_BITFINEX_ORDER = '/v1/order/new'

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
