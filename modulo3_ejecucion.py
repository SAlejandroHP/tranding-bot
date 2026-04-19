import os
import ccxt
from dotenv import load_dotenv

# Configurar variables de entorno como en los módulos anteriores
load_dotenv()
api_key = os.getenv("BITSO_API_KEY")
api_secret = os.getenv("BITSO_SECRET")

def comprar_100_porciento(exchange, simbolo='BTC/MXN'):
    try:
        # Obtener el saldo disponible (free) de 'MXN'
        balance = exchange.fetch_balance()
        saldos_libres = balance.get('free', {})
        saldo_mxn = saldos_libres.get('MXN', 0.0)

        # Si el saldo es menor a $100 MXN, cancelar
        if saldo_mxn < 100:
            print(f"No hay fondos suficientes para comprar de forma segura. Saldo actual: ${saldo_mxn} MXN. Se cancela la operación.")
            return

        # Obtener el precio actual del 'Ask'
        order_book = exchange.fetch_order_book(simbolo)
        precio_ask = order_book['asks'][0][0] if len(order_book['asks']) > 0 else None
        
        if not precio_ask:
            print("No se pudo obtener el 'Ask' del order book. Se cancela la operación.")
            return

        # Calcular la cantidad de BTC a comprar con margen de seguridad (0.99)
        cantidad_btc = (saldo_mxn / precio_ask) * 0.99

        # Ejecutar la orden de compra de mercado
        orden = exchange.create_market_buy_order(simbolo, cantidad_btc)
        
        # Imprimir mensaje de éxito
        print(f"✅ ¡Éxito! Orden de compra ejecutada. Cantidad comprada: {cantidad_btc} BTC a un precio aproximado de ${precio_ask} MXN.")
        
    except ccxt.BaseError as e:
        print(f"❌ Error en el exchange al ejecutar compra: {e}")
    except Exception as e:
        print(f"❌ Error inesperado al ejecutar compra: {e}")

def vender_100_porciento(exchange, simbolo='BTC/MXN'):
    try:
        # Obtener el saldo disponible (free) de 'BTC'
        balance = exchange.fetch_balance()
        saldos_libres = balance.get('free', {})
        saldo_btc = saldos_libres.get('BTC', 0.0)

        # Si el saldo es mayor a 0.0001, ejecutar venta
        if saldo_btc > 0.0001:
            orden = exchange.create_market_sell_order(simbolo, saldo_btc)
            print(f"✅ ¡Éxito! Posición cerrada. Se vendieron {saldo_btc} BTC.")
        else:
            print(f"Saldo insuficiente para vender. Saldo actual de {saldo_btc} BTC (por debajo del límite/dust de 0.0001 BTC).")

    except ccxt.BaseError as e:
        print(f"❌ Error en el exchange al ejecutar venta: {e}")
    except Exception as e:
        print(f"❌ Error inesperado al ejecutar venta: {e}")

# NO ejecutar las funciones automáticamente
print("Módulo de ejecución listo y cargado")
