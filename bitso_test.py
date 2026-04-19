import ccxt

exchange = ccxt.bitso({'apiKey': 'dummy', 'secret': 'dummy'})
try:
    exchange.create_market_buy_order('LTC/MXN', 0.1)
except Exception as e:
    print(str(e))
