import os
from dotenv import load_dotenv
from crewai import Agent, Task, Crew, Process, LLM

# Cargar variables de entorno
load_dotenv()

# Instancia global del LLM para los agentes (analítico y frío)
llm_groq = LLM(
    model="groq/llama-3.3-70b-versatile",
    temperature=0.1
)

# --- 1. DEFINICIÓN DE AGENTES ---

agente_analista = Agent(
    role='Analista Cuantitativo',
    goal='Seleccionar 1 activo ideal sin decir una palabra extra.',
    backstory='Eres un robot algoritmico. Tus respuestas nunca superan las 15 palabras. Das el activo y el punto clave.',
    verbose=True,
    llm=llm_groq
)

agente_riesgos = Agent(
    role='Auditor de Comisiones',
    goal='Calcular breakeven con comisiones de Maker/Taker.',
    backstory='Eres una calculadora veloz. No escribes texto introductorio. Devuelves el Breakeven neto y si es viable o no.',
    verbose=True,
    llm=llm_groq
)

agente_ceo = Agent(
    role='CEO Final (Generador JSON)',
    goal='Emitir veredicto en formato de datos plano.',
    backstory='Eres un intérprete de máquina a máquina. Tomas el reporte de análisis y el riesgo, y escupes un JSON estrictamente válido. Odias la cortesía y el formato Markdown. Cero prosa.',
    verbose=True,
    llm=llm_groq
)

# --- 2. DEFINICIÓN DE TAREAS ---

tarea_analisis = Task(
    description='Estrategia: {estrategia_actual}. Activos pre-filtrados (cuantitativamente aprobados): {datos_mercado}. Evalúa y elige 1.',
    expected_output='El SIMBOLO exacto y máximo 10 palabras del motivo cualitativo.',
    agent=agente_analista
)

tarea_riesgo = Task(
    description='Saldo: ${saldo_actual} MXN. Taker Fee: {taker_fee_pct}%. Calcula el precio de Breakeven. Adicionalmente, basándote en lo estrecho del % de ganancia de Scalping (y las altas comisiones), evalúa y define de cuánto debería ser la inversión inicial mínima (MXN) para que valga la pena obtener ganancias monetarias.',
    expected_output='Breakeven, Veredicto (Máx 15 palab) y "Capital mínimo sugerido: XXX MXN".',
    agent=agente_riesgos
)

tarea_decision = Task(
    description='Revisa datos de Analista y Riesgo. Genera la orden inexcusablemente. Siempre debe ser aprobada bajo tu propio riesgo directivo.',
    expected_output='ESTRICTO RAW JSON, SIN MARKDOWN (```json): {{"simbolo": "ACTIVO/MXN", "razon": "Max 5 palab", "precio_entrada_sugerido": 0.0, "breakeven_calculado": 0.0, "aprobado": true, "inversion_minima_sugerida": 0.0}}',
    agent=agente_ceo
)

# --- 3. ENSAMBLAJE DEL CREW ---

junta_directiva = Crew(
    agents=[agente_analista, agente_riesgos, agente_ceo],
    tasks=[tarea_analisis, tarea_riesgo, tarea_decision],
    process=Process.sequential,
    verbose=True
)

# --- 4. FUNCIÓN PRINCIPAL DE EJECUCIÓN ---

def ejecutar_junta_directiva(datos_mercado_str, saldo_mxn, estrategia_actual, taker_fee=0.0065):
    print(f"🚀 Iniciando sesión de la Junta Directiva de SaaK Solutions (Estrategia: {estrategia_actual})...")
    
    inputs = {
        'datos_mercado': datos_mercado_str,
        'saldo_actual': saldo_mxn,
        'estrategia_actual': estrategia_actual,
        'taker_fee_pct': round(taker_fee * 100, 3)
    }
    
    resultado = junta_directiva.kickoff(inputs=inputs)
    return resultado

if __name__ == "__main__":
    import ccxt
    
    # Datos simulados para probar la intuición de la Junta Directiva
    datos_prueba = '''
    BTC/MXN: RSI=65, Volatilidad=Baja, Tendencia=Estable (Activo muy pesado).
    SOL/MXN: RSI=42, Volatilidad=Alta, Tendencia=Alcista, a punto de romper resistencia de $1,500.
    ETH/MXN: RSI=82, Volatilidad=Media, Tendencia=Sobrecomprado. Peligro de corrección.
    '''
    
    saldo_prueba = 1000.00
    try:
        api_key = os.getenv("BITSO_API_KEY")
        api_secret = os.getenv("BITSO_SECRET")
        if api_key and api_secret:
            exchange = ccxt.bitso({
                'apiKey': api_key,
                'secret': api_secret,
                'enableRateLimit': True,
            })
            balance = exchange.fetch_balance()
            mxn_free = float(balance.get('MXN', {}).get('free', 0.0))
            saldo_prueba = mxn_free
                
            print(f"Saldo real de Bitso obtenido para la prueba: ${saldo_prueba:,.2f} MXN equivalentes.")
        else:
            print("No se encontraron credenciales de Bitso, usando 1000 MXN para prueba.")
    except Exception as e:
        print(f"Error obteniendo saldo de Bitso para prueba: {e}")
    
    # Asegurarnos de que el saldo de prueba sea mayor a 0 para que no falle
    if saldo_prueba <= 0:
        saldo_prueba = 1000.00

    resultado_final = ejecutar_junta_directiva(datos_prueba, saldo_prueba, "Swing", 0.0065)
    
    print("\n=== DICTAMEN FINAL DEL CEO ===")
    print(resultado_final)
