import yfinance as yf
import pandas as pd

def descargar_datos_historicos():
    """
    Descarga 2 años de datos históricos diarios calculando el par BTC-MXN de forma sintética.
    Como Yahoo a veces deslista el par directo, obtenemos BTC-USD y MXN=X y los multiplicamos.
    """
    try:
        df_btc = yf.Ticker("BTC-USD").history(period="2y", interval="1d")
        df_mxn = yf.Ticker("MXN=X").history(period="2y", interval="1d")
        
        if df_btc.empty:
            print("Advertencia: Se completó la solicitud pero no se obtuvieron datos históricos.")
            return pd.DataFrame()
            
        # Normalizar índices (remover timezone) para alinear fechas de BTC y Forex
        df_btc.index = df_btc.index.tz_localize(None).normalize()
        df_mxn.index = df_mxn.index.tz_localize(None).normalize()
        
        # Filtrar los 'Close', 'High' y 'Low'
        df_btc = df_btc[['Close', 'High', 'Low']].rename(columns={'Close': 'precio', 'High': 'alto', 'Low': 'bajo'})
        df_mxn = df_mxn[['Close']].rename(columns={'Close': 'tipo_cambio'})
        
        # Unir usando el índice de BTC (que incluye fines de semana)
        df_combinado = df_btc.join(df_mxn)
        
        # Rellenar fines de semana de Forex (tipo de cambio)
        df_combinado['tipo_cambio'] = df_combinado['tipo_cambio'].ffill().bfill()
        
        # Calcular BTC en MXN
        df_combinado['precio'] = df_combinado['precio'] * df_combinado['tipo_cambio']
        df_combinado['alto'] = df_combinado['alto'] * df_combinado['tipo_cambio']
        df_combinado['bajo'] = df_combinado['bajo'] * df_combinado['tipo_cambio']
        
        return df_combinado[['precio', 'alto', 'bajo']]
        
    except Exception as e:
        print(f"Error de conexión o de descarga de datos: {e}")
        return pd.DataFrame()

def aplicar_estrategia_rsi(df):
    """
    Calcula el RSI de 14 periodos y el Filtro de Volatilidad (ATR).
    La 'Senal_Compra' se activa si (RSI < 30) Y (ATR_pct > margen_operacion).
    """
    comision_exchange = 0.002
    margen_minimo = 0.005
    margen_operacion = (comision_exchange * 2) + margen_minimo

    df_estrategia = df.copy()
    
    # Calcular RSI de 14 periodos usando media móvil exponencial (Wilder)
    delta = df_estrategia['precio'].diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    avg_gain = gain.ewm(alpha=1/14, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1/14, adjust=False).mean()
    rs = avg_gain / avg_loss
    df_estrategia['RSI'] = 100 - (100 / (1 + rs))
    
    # Calcular ATR de 14 periodos
    df_estrategia['prev_precio'] = df_estrategia['precio'].shift(1)
    df_estrategia['tr1'] = df_estrategia['alto'] - df_estrategia['bajo']
    df_estrategia['tr2'] = (df_estrategia['alto'] - df_estrategia['prev_precio']).abs()
    df_estrategia['tr3'] = (df_estrategia['bajo'] - df_estrategia['prev_precio']).abs()
    df_estrategia['TR'] = df_estrategia[['tr1', 'tr2', 'tr3']].max(axis=1)
    df_estrategia['ATR'] = df_estrategia['TR'].rolling(window=14).mean()
    df_estrategia['ATR_pct'] = df_estrategia['ATR'] / df_estrategia['precio']
    
    # Limpiar columnas temporales
    df_estrategia.drop(columns=['prev_precio', 'tr1', 'tr2', 'tr3', 'TR'], inplace=True)
    
    # Rellenar nulos iniciales de las medias
    df_estrategia.dropna(inplace=True)
    
    # Señal cuando RSI < 30 y ATR_pct > margen_operacion
    df_estrategia['Senal_Compra'] = ((df_estrategia['RSI'] < 30) & (df_estrategia['ATR_pct'] > margen_operacion)).astype(int)
    
    return df_estrategia

def simular_ejecucion(df):
    """
    Simula la ejecución de la estrategia iterando sobre el DataFrame.
    Implementa un Filtro de Volatilidad y Take-Profit dinámico basado en costos.
    """
    en_posicion = False
    precio_compra = 0.0
    comision_exchange = 0.002
    margen_minimo = 0.005
    margen_operacion = (comision_exchange * 2) + margen_minimo
    
    trades = []
    df_sim = df.copy()
    
    precio_inicial = df_sim['precio'].iloc[0]
    precio_final = df_sim['precio'].iloc[-1]
    rendimiento_hold = (precio_final / precio_inicial) - 1
    
    for fecha, row in df_sim.iterrows():
        precio_actual = row['precio']
        senal_compra = row['Senal_Compra']
        
        if not en_posicion:
            if senal_compra == 1:
                en_posicion = True
                precio_compra = precio_actual
        else:
            # Criterios de salida
            tp_alcanzado = precio_actual >= precio_compra * (1 + margen_operacion)
            sl_alcanzado = precio_actual <= precio_compra * (1 - 0.03)
            
            if tp_alcanzado or sl_alcanzado:
                en_posicion = False
                rendimiento_actual = (precio_actual / precio_compra) - 1
                # Calculo del retorno neto: Restamos comisiones de entrada y salida
                retorno_neto = rendimiento_actual - (comision_exchange * 2)
                trades.append(retorno_neto)
                
    rendimiento_ia = 1.0
    ganadoras = 0
    perdedoras = 0
    
    for t in trades:
        rendimiento_ia *= (1 + t)
        if t > 0:
            ganadoras += 1
        else:
            perdedoras += 1
            
    rendimiento_ia -= 1
    total_operaciones = len(trades)
    
    print("\n========= RESULTADOS DEL BACKTEST =========")
    print(f"Rendimiento Hold (%): {rendimiento_hold * 100:.2f}%")
    print(f"Rendimiento IA (%):   {rendimiento_ia * 100:.2f}%")
    print(f"Total de Operaciones Realizadas: {total_operaciones}")
    if total_operaciones > 0:
        print(f"Operaciones Ganadoras: {ganadoras} ({(ganadoras/total_operaciones)*100:.1f}%)")
        print(f"Operaciones Perdedoras: {perdedoras} ({(perdedoras/total_operaciones)*100:.1f}%)")
    else:
        print("Operaciones Ganadoras: 0")
        print("Operaciones Perdedoras: 0")
    print("===========================================\n")
    
    return df_sim

if __name__ == "__main__":
    # Ejecutamos las tres funciones secuencialmente (El ciclo completo)
    print("Iniciando Módulo 0: Backtest de Trading Bot...")
    
    # Fase 1: Descarga
    df_btc = descargar_datos_historicos()
    
    if not df_btc.empty:
        # Fase 2: Estrategia
        df_estrategia = aplicar_estrategia_rsi(df_btc)
        
        # Fase 3: Simulación y Rendimiento
        df_resultados = simular_ejecucion(df_estrategia)
    else:
        print("Error: DataFrame vacío. Saliendo...")
