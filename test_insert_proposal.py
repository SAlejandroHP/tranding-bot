import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv(".env")
url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")
supabase = create_client(url, key)

res = supabase.table("trade_proposals").insert({
    'simbolo': 'BTC/MXN',
    'estrategia': 'Swing',
    'proyeccion': 'Fuerte ineficiencia detectada por la Junta Directiva (CrewAI). RSI favorable y volumen institucional. (Min Sugerido: $1,500.00 MXN)',
    'probabilidad': 88,
    'precio_entrada': 1300000.00,
    'status': 'pendiente'
}).execute()

print("Mock proposal inserted.")
