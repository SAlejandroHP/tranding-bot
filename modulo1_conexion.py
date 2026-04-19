import os
import ccxt
from dotenv import load_dotenv

# Cargar variables de entorno desde el archivo .env
load_dotenv()

def verificar_conexion_y_saldos(exchange):
    """
    Verifica la conexión con el exchange, consulta los saldos de BTC y MXN,
    y obtiene el precio actual (Ask/Bid) del par BTC/MXN a través del Order Book.
    """
    try:
        print("Iniciando conexión segura con el exchange...")
        
        # Cargar los mercados sirve como prueba inicial de conexión
        exchange.load_markets()
        print("✅ Conexión exitosa con el exchange de Bitso.\n")

        # Consultar y mostrar el saldo disponible (free) de 'MXN' y 'BTC'
        print("--- Consultando Saldos Disponibles ---")
        balance = exchange.fetch_balance()
        saldos_libres = balance.get('free', {})
        
        saldo_mxn = saldos_libres.get('MXN', 0.0)
        saldo_btc = saldos_libres.get('BTC', 0.0)
        
        print(f"Saldo MXN: {saldo_mxn}")
        print(f"Saldo BTC: {saldo_btc}\n")

        # Consultar el 'Order Book' del par 'BTC/MXN'
        print("--- Consultando Order Book: BTC/MXN ---")
        symbol = 'BTC/MXN'
        order_book = exchange.fetch_order_book(symbol)
        
        # El Ask más bajo es el mejor precio para comprar
        lowest_ask = order_book['asks'][0][0] if len(order_book['asks']) > 0 else None
        
        # El Bid más alto es el mejor precio para vender
        highest_bid = order_book['bids'][0][0] if len(order_book['bids']) > 0 else None
        
        print(f"Precio del Ask más bajo (Mejor para comprar): ${lowest_ask:,.2f} MXN")
        print(f"Precio del Bid más alto (Mejor para vender):  ${highest_bid:,.2f} MXN")
        print("\n✅ Datos del mercado en vivo leídos correctamente.")

    except ccxt.AuthenticationError as e:
        print(f"❌ Error de Autenticación: Verifica que tus llaves API (BITSO_API_KEY y BITSO_SECRET) sean correctas y tengan los permisos adecuados.\nDetalles: {e}")
    except ccxt.NetworkError as e:
        print(f"❌ Error de Red: Hubo un problema conectándose con los servidores de Bitso.\nDetalles: {e}")
    except ccxt.ExchangeError as e:
        print(f"❌ Error del Exchange: Falló alguna operación con Bitso.\nDetalles: {e}")
    except Exception as e:
        print(f"❌ Error Inesperado al verificar la conexión y los saldos.\nDetalles: {e}")

if __name__ == "__main__":
    # 1. Recuperar llaves del entorno
    api_key = os.getenv("BITSO_API_KEY")
    api_secret = os.getenv("BITSO_SECRET")
    
    if not api_key or not api_secret:
        print("⚠️ Advertencia: No se encontraron 'BITSO_API_KEY' o 'BITSO_SECRET' en el entorno.")
        print("Asegúrate de que estás cargando correctamente el archivo .env")

    # 2. Configurar la instancia del exchange para Bitso
    bitso_exchange = ccxt.bitso({
        'apiKey': api_key,
        'secret': api_secret,
        'enableRateLimit': True, # Recomendado siempre para evitar baneos por límite de peticiones
    })

    # 3. Ejecutar la función de prueba
    verificar_conexion_y_saldos(bitso_exchange)
