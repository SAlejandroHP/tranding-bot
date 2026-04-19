import os
import ccxt
from dotenv import load_dotenv

def obtener_fees_dinamicos(exchange, symbol='BTC/MXN'):
    """
    Obtiene las comisiones (fees) de forma dinámica desde el exchange.
    Retorna una tupla (maker_fee, taker_fee) en formato decimal (ej: 0.006 para 0.6%).
    En caso de error, retorna un fallback prudente (0.0065 para Bitso).
    """
    try:
        if not exchange.markets:
            exchange.load_markets()
            
        maker_fee = None
        taker_fee = None

        if symbol in exchange.markets:
            maker_fee = exchange.markets[symbol].get('maker')
            taker_fee = exchange.markets[symbol].get('taker')
        
        if maker_fee is None or taker_fee is None:
            if exchange.has.get('fetchTradingFee'):
                fee_info = exchange.fetch_trading_fee(symbol)
                maker_fee = fee_info.get('maker')
                taker_fee = fee_info.get('taker')
            elif exchange.has.get('fetchTradingFees'):
                fees_info = exchange.fetch_trading_fees()
                if symbol in fees_info:
                    maker_fee = fees_info[symbol].get('maker')
                    taker_fee = fees_info[symbol].get('taker')

        # Fallbacks a default (Bitso highest volume tier es menos, pero para proteccion de fallback usamos 0.65%)
        # Convertimos a float si eran numericos
        maker_val = float(maker_fee) if maker_fee is not None else 0.0065
        taker_val = float(taker_fee) if taker_fee is not None else 0.0065

        return maker_val, taker_val

    except Exception as e:
        print(f"⚠️ Error obteniendo fees dinámicos para {symbol}: {e}. Usando fallback 0.65%.")
        return 0.0065, 0.0065

if __name__ == "__main__":
    # Test local
    load_dotenv()
    api_key = os.getenv('BITSO_API_KEY')
    secret = os.getenv('BITSO_SECRET')
    if api_key and secret:
        ex = ccxt.bitso({'apiKey': api_key, 'secret': secret, 'enableRateLimit': True})
        m, t = obtener_fees_dinamicos(ex, 'BTC/MXN')
        print(f"Test Fees -> Maker: {m*100:.2f}%, Taker: {t*100:.2f}%")
