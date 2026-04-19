import os
from dotenv import load_dotenv
load_dotenv()
import time
import ccxt
import pandas as pd
import json
import requests
from supabase import create_client, Client
from groq import Groq


def obtener_velas_bitso(exchange, simbolo='BTC/MXN', timeframe='15m', limite=100):
    """
    Descarga el histórico de velas para un símbolo usando ccxt.
    Devuelve un DataFrame con las columnas adecuadas.
    """
    print(f"Descargando últimas {limite} velas de {simbolo}...")
    velas = exchange.fetch_ohlcv(symbol=simbolo, timeframe=timeframe, limit=limite)
    
    # Crear DataFrame
    df = pd.DataFrame(velas, columns=['fecha', 'Open', 'High', 'Low', 'Close', 'Volume'])
    
    # Convertir timestamp a formato de fecha legible
    df['fecha'] = pd.to_datetime(df['fecha'], unit='ms')
    
    return df

def calcular_indicadores_vivos(df):
    """
    Calcula el RSI (14 periodos) y el ATR (14 periodos) sobre el DataFrame en vivo.
    """
    df_est = df.copy()
    
    # --- Calcular RSI de 14 periodos ---
    delta = df_est['Close'].diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    avg_gain = gain.ewm(alpha=1/14, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1/14, adjust=False).mean()
    rs = avg_gain / avg_loss
    df_est['RSI'] = 100 - (100 / (1 + rs))
    
    # --- Calcular ATR de 14 periodos ---
    df_est['prev_Close'] = df_est['Close'].shift(1)
    df_est['tr1'] = df_est['High'] - df_est['Low']
    df_est['tr2'] = (df_est['High'] - df_est['prev_Close']).abs()
    df_est['tr3'] = (df_est['Low'] - df_est['prev_Close']).abs()
    
    # True Range es el máximo de estos 3
    df_est['TR'] = df_est[['tr1', 'tr2', 'tr3']].max(axis=1)
    
    # ATR es la media móvil simple de 14 periodos del TR
    df_est['ATR'] = df_est['TR'].rolling(window=14).mean()
    
    # ATR_pct: para evaluar la volatilidad relativa al precio actual
    df_est['ATR_pct'] = df_est['ATR'] / df_est['Close']
    
    # Limpiar columnas intermedias
    df_est.drop(columns=['prev_Close', 'tr1', 'tr2', 'tr3', 'TR'], inplace=True)
    
    # --- Calcular SMA de 20 periodos ---
    df_est['SMA_20'] = df_est['Close'].rolling(window=20).mean()
    
    return df_est

def generar_propuestas_ia(estrategia_activa):
    """
    Obtiene dinámicamente los mercados en Bitso, selecciona los 10 con mayor volumen,
    y envía un prompt a Gemini para obtener una terna de 3 candidatos basada en la estrategia.
    """
    # Conectar a Bitso
    api_key = os.getenv("BITSO_API_KEY")
    api_secret = os.getenv("BITSO_SECRET")
    exchange = ccxt.bitso({
        'apiKey': api_key,
        'secret': api_secret,
        'enableRateLimit': True,
    })
    
    print("Obteniendo estado actual de los mercados en Bitso...")
    try:
        response = exchange.publicGetTicker()
        tickers = response.get('payload', [])
    except Exception as e:
        print(f"Error al obtener tickers de Bitso: {e}")
        return []

    # Filtrar pares MXN y calcular volumen cotizado
    mercados_mxn = []
    
    for ticker_data in tickers:
        book = ticker_data.get('book', '')
        if book.endswith('_mxn'):
            symbol = book.replace('_', '/').upper()
            precio_actual = ticker_data.get('last')
            volumen_base = ticker_data.get('volume', 0)
            
            if precio_actual is not None and volumen_base is not None:
                try:
                    vol_quote = float(volumen_base) * float(precio_actual)
                    mercados_mxn.append({
                        'symbol': symbol,
                        'precio': float(precio_actual),
                        'volumen': vol_quote
                    })
                except ValueError:
                    pass
                    
    # Ordenar por volumen de mayor a menor y tomar solo los primeros 10
    mercados_mxn.sort(key=lambda x: x['volumen'], reverse=True)
    top_10 = mercados_mxn[:10]

    lista_datos = []
    precios_actuales = {}

    for m in top_10:
        lista_datos.append(f"- {m['symbol']}: {m['precio']}")
        precios_actuales[m['symbol']] = m['precio']
                
    resumen_mercados = "\n".join(lista_datos)
    
    print("Iniciando solicitud a Groq API (llama-3.3-70b-versatile)...")
    client = Groq(api_key=os.getenv("GROQ_API_KEY"))
    
    # Bucle de reintentos
    for intento in range(3):
        try:
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {
                        "role": "system",
                        "content": "Eres un analista cuantitativo. DEBES responder ÚNICA Y EXCLUSIVAMENTE con un array JSON válido de 3 objetos. No añadas texto introductorio, ni conclusiones, ni formateo Markdown. Solo los corchetes y llaves del JSON."
                    },
                    {
                        "role": "user",
                        "content": f"Este es el catálogo de los top 10 mercados principales en vivo de Bitso hoy:\n{resumen_mercados}\n\nEl usuario quiere aplicar la estrategia: {estrategia_activa}. Evalúa qué 3 criptomonedas tienen el mayor potencial para esta estrategia hoy. Cada objeto del JSON debe contener: 'simbolo' (debe incluir /MXN), 'proyeccion' (por qué la elegiste, 1 línea corta) y 'probabilidad' (entero 0-100)."
                    }
                ],
                temperature=0.2
            )
            
            texto = response.choices[0].message.content.strip()
            
            if texto.startswith("```json"):
                texto = texto[7:-3].strip()
            elif texto.startswith("```"):
                texto = texto[3:-3].strip()
                
            propuestas = json.loads(texto)
            for p in propuestas:
                simbolo = p.get('simbolo', '')
                if simbolo in precios_actuales:
                    p['precio_entrada'] = float(precios_actuales[simbolo])
                else:
                    p['precio_entrada'] = 0.0
                    
            return propuestas
        except Exception as e:
            print(f"Error real de Groq: {e}")
            time.sleep(5)
            
    print("Error crítico con Gemini después de 3 intentos.")
    print("Devolviendo lista vacía para forzar tiempo de espera y proteger la API.")
    return []

def seleccionar_activo_por_ia(estrategia):
    """
    Decide el mejor activo para operar basado en la estrategia usando IA.
    """
    try:
        client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        prompt = f"Eres un Portfolio Manager. El usuario seleccionó la estrategia {estrategia}. Tienes este catálogo de pares en Bitso: BTC/MXN, ETH/MXN, SOL/MXN, XRP/MXN, DOGE/MXN, SHIB/MXN. Para Hold busca máxima solidez histórica. Para Swing busca momentum tendencial. Para Scalping busca la máxima volatilidad intradía. Basado en tu conocimiento del comportamiento de estos activos, ¿cuál es el mejor par para operar hoy? Responde con el string del par elegido y una explicación máxima de 2 líneas separados por un pipe (|), por ejemplo: 'SOL/MXN | Se observa una formación de bandera alcista en temporalidad de 15m con RSI saliendo de sobreventa; alta probabilidad de rebote técnico.'"
        
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "Eres un asistente de Inteligencia Artificial que siempre responde siguiendo las reglas indicadas."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2
        )
        texto = response.choices[0].message.content.replace('`', '').strip()
        
        if '|' in texto:
            partes = texto.split('|')
            simbolo = partes[0].strip().upper()
            proyeccion = partes[1].strip()
            if '/' in simbolo:
                return simbolo, proyeccion
        else:
            simbolo = texto.strip().upper()
            if '/' in simbolo:
                return simbolo, "Sin proyección (formato inesperado)"
    except Exception as e:
        print(f"Error con Groq API al seleccionar activo: {e}")
    
    return "BTC/MXN", "Predeterminado - Sin IA o error"

def evaluar_mercado_actual(simbolo_actual='BTC/MXN'):
    """
    Función principal: conecta, descarga, analiza y muestra el dashboard en vivo.
    """
    try:
        # 1. Recuperar llaves del entorno y conectar
        api_key = os.getenv("BITSO_API_KEY")
        api_secret = os.getenv("BITSO_SECRET")
        
        if not api_key or not api_secret:
            raise ValueError("No se encontraron 'BITSO_API_KEY' o 'BITSO_SECRET' en el entorno.")
            
        exchange = ccxt.bitso({
            'apiKey': api_key,
            'secret': api_secret,
            'enableRateLimit': True,
        })
        
        # 2. Descargar velas
        df = obtener_velas_bitso(exchange, simbolo=simbolo_actual, timeframe='15m', limite=100)
        
        # 3. Calcular indicadores
        df_indicadores = calcular_indicadores_vivos(df)
        
        # Inicializar Supabase para leer la estrategia
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_KEY")
        estrategia_activa = "Hold"
        if supabase_url and supabase_key:
            try:
                supabase = create_client(supabase_url, supabase_key)
                respuesta = supabase.table('bot_status').select('estrategia_activa').eq('id', 1).execute()
                if respuesta.data and 'estrategia_activa' in respuesta.data[0]:
                    estrategia_activa = respuesta.data[0]['estrategia_activa']
            except Exception as e:
                print(f"Error al leer estrategia de Supabase: {e}")

        # 4. Extraer valores de la ÚLTIMA vela cerrada (índice -2 en el DataFrame)
        ultima_vela_cerrada = df_indicadores.iloc[-2]
        
        fecha = ultima_vela_cerrada['fecha']
        precio_cierre = ultima_vela_cerrada['Close']
        rsi_actual = ultima_vela_cerrada['RSI']
        atr_pct = ultima_vela_cerrada['ATR_pct']
        sma_20 = ultima_vela_cerrada['SMA_20']
        
        # Consultar IA (Groq)
        probabilidad = 50
        try:
            client = Groq(api_key=os.getenv("GROQ_API_KEY"))
            prompt = f"Eres un modelo de inferencia de trading. La estrategia actual es {estrategia_activa}. El precio actual es {precio_cierre}. El RSI es {rsi_actual}. La volatilidad ATR es {atr_pct}. Basado en estos parámetros cuantitativos, evalúa la probabilidad de una ruptura alcista. Responde ÚNICAMENTE con un número entero del 0 al 100 representando el porcentaje de probabilidad. No justifiques tu respuesta."
            
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": "Eres un asistente cuantitativo puro y preciso."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1
            )
            texto = response.choices[0].message.content.strip()
            
            # Try to extract the first number found
            import re
            numbers = re.findall(r'\d+', texto)
            if numbers:
                probabilidad = int(numbers[0])
            else:
                probabilidad = 50
        except Exception as e:
            print(f"Error con Groq API: {e}")
                
        # 5. Determinar la SEÑAL ACTUAL usando la lógica híbrida
        senal = "⏸️ HOLD / ESPERAR"
        return_senal = "HOLD"

        if estrategia_activa == 'Scalping':
            if rsi_actual < 40 and probabilidad > 75:
                senal = "✅ COMPRAR (Scalping)"
                return_senal = "COMPRAR"
            elif rsi_actual >= 70:
                senal = "❌ VENDER"
                return_senal = "VENDER"
        elif estrategia_activa == 'Swing':
            if rsi_actual < 30 and probabilidad > 80:
                senal = "✅ COMPRAR (Swing)"
                return_senal = "COMPRAR"
            elif rsi_actual >= 70:
                senal = "❌ VENDER"
                return_senal = "VENDER"
        else: # Hold o predeterminado
            if pd.notna(sma_20) and precio_cierre <= sma_20 * 0.95:
                senal = "✅ COMPRAR (DCA Hold)"
                return_senal = "COMPRAR"
            elif rsi_actual >= 70:
                senal = "❌ VENDER"
                return_senal = "VENDER"

        # 6. Imprimir Dashboard en Vivo
        print("\n==========================================")
        print("          DASHBOARD EN VIVO")
        print("==========================================")
        print(f"Fecha Vela Cerrada: {fecha}")
        print(f"Precio Cierre:      ${precio_cierre:,.2f} MXN")
        print(f"RSI (14 periodos):  {rsi_actual:.2f}")
        print(f"Volatilidad (ATR):  {atr_pct*100:.2f}%")
        print(f"SMA (20 periodos):  ${sma_20:,.2f} MXN")
        print(f"Estrategia:         {estrategia_activa}")
        print(f"Prob. Ruptura (IA): {probabilidad}%")
        print("------------------------------------------")
        print(f"SEÑAL ACTUAL:       {senal}")
        print(f"ACTIVO OPERADO:     {simbolo_actual}")
        print("==========================================\n")

        return return_senal, rsi_actual, atr_pct, probabilidad

    except ValueError as ve:
        print(f"❌ Error de Configuración: {ve}")
        return "ERROR", 0.0, 0.0, 0
    except ccxt.BaseError as ce:
        print(f"❌ Error de Conexión o API con Bitso: {ce}")
        return "ERROR", 0.0, 0.0, 0
    except Exception as e:
        print(f"❌ Error Inesperado al evaluar el mercado: {e}")
        return "ERROR", 0.0, 0.0, 0

if __name__ == "__main__":
    evaluar_mercado_actual()
