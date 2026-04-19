import ccxt
import json

exchange = ccxt.bitso({'apiKey': 'dummy', 'secret': 'dummy'})
try:
    print(exchange.create_market_buy_order.__doc__)
except Exception as e:
    pass
