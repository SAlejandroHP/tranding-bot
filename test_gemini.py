import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

def seleccionar_activo_por_ia(estrategia):
    gemini_api_key = os.getenv("VITE_GEMINI_API_KEY") or os.getenv("GEMINI_API_KEY")
    if gemini_api_key:
        try:
            client = genai.Client(api_key=gemini_api_key)
            prompt = f"Eres un Portfolio Manager. El usuario seleccionó la estrategia {estrategia}. Tienes este catálogo de pares en Bitso: BTC/MXN, ETH/MXN, SOL/MXN, XRP/MXN, DOGE/MXN, SHIB/MXN. Para Hold busca máxima solidez histórica. Para Swing busca momentum tendencial. Para Scalping busca la máxima volatilidad intradía. Basado en tu conocimiento del comportamiento de estos activos, ¿cuál es el mejor par para operar hoy? Responde con el string del par elegido y una explicación máxima de 2 líneas separados por un pipe (|), por ejemplo: 'SOL/MXN | Se observa una formación de bandera alcista en temporalidad de 15m con RSI saliendo de sobreventa; alta probabilidad de rebote técnico.'"
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=prompt
            )
            texto = response.text.replace('`', '').strip()
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
            print(f"Error con Gemini al seleccionar activo: {e}")
    
    return "BTC/MXN", "Predeterminado - Sin IA o error"

print(seleccionar_activo_por_ia("Swing"))
