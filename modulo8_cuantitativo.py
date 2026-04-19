import pandas as pd
import numpy as np

def calcular_rsi(series, periodos=14):
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=periodos).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=periodos).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

def calcular_macd(series, slow=26, fast=12, signal=9):
    exp1 = series.ewm(span=fast, adjust=False).mean()
    exp2 = series.ewm(span=slow, adjust=False).mean()
    macd = exp1 - exp2
    signal_line = macd.ewm(span=signal, adjust=False).mean()
    histogram = macd - signal_line
    return macd, signal_line, histogram

def realizar_analisis_tecnico(exchange, simbolo, timeframe='15m', limit=50):
    try:
        ohlcv = exchange.fetch_ohlcv(simbolo, timeframe, limit=limit)
        if not ohlcv or len(ohlcv) < 30:
            return None
            
        df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        
        # Calcular indicadores
        df['rsi'] = calcular_rsi(df['close'])
        macd, signal, hist = calcular_macd(df['close'])
        df['macd'] = macd
        df['macd_signal'] = signal
        df['macd_hist'] = hist
        
        # Calcular media de volumen
        df['vol_ma'] = df['volume'].rolling(window=20).mean()
        
        # Ultima vela (vela actual o cerrada reciente)
        curr = df.iloc[-1]
        
        # Criterios cuantitativos de ejemplo
        is_oversold = curr['rsi'] < 40  # RSI bajo
        is_macd_bullish = curr['macd_hist'] > 0 and df.iloc[-2]['macd_hist'] <= 0 # MACD cruce alcista
        high_volume = curr['volume'] > (curr['vol_ma'] * 1.2) # Spike de volumen
        
        # Determinar si "Pasa" el filtro verde
        # Para Hold/Swing: Buscamos sobreventa (RSI < 40) o cruce alcista
        # Para Scalping: Buscamos volatilidad y momento de volumen
        
        puntaje = 0
        razones = []
        
        if is_oversold:
            puntaje += 1
            razones.append("RSI en zona de sobreventa (<40)")
        if curr['rsi'] > 60:
            razones.append("RSI alto, cuidado")
            puntaje -= 1
        if is_macd_bullish:
            puntaje += 2
            razones.append("Cruce MACD Alcista detectado")
        if high_volume:
            puntaje += 1
            razones.append("Incremento inusual de volumen")
            
        # Consideramos "apto" si el puntaje es >= 1
        return {
            'simbolo': simbolo,
            'precio': curr['close'],
            'rsi': round(curr['rsi'], 2),
            'apto': puntaje >= 1,
            'puntaje': puntaje,
            'razones': razones
        }
        
    except Exception as e:
        if "bitso does not have market symbol" in str(e) or "bad symbol" in str(e).lower():
            print(f"⚠️ Moneda no soportada en Exchange actual ({simbolo}), saltando análisis...")
        else:
            print(f"Error en análisis cuantitativo para {simbolo}: {e}")
        return None
