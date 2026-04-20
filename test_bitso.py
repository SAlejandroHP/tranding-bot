import sys
import ccxt
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("BITSO_API_KEY")
api_secret = os.getenv("BITSO_SECRET")

exchange = ccxt.bitso({
    'apiKey': api_key,
    'secret': api_secret,
    'enableRateLimit': True,
})

balance = exchange.fetch_balance()
print("MXN Balance:", balance.get('MXN', {}).get('free', 0.0))
