import os
import sys
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()
url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")
if not url or not key:
    print("Faltan credenciales DB")
    sys.exit(1)

client = create_client(url, key)

# Limpiar todas las posiciones
res1 = client.table('open_positions').select('id').execute()
for r in res1.data:
    client.table('open_positions').delete().eq('id', r['id']).execute()

# Limpiar logs de operaciones (trades)
res3 = client.table('trades_log').select('id').execute()
for r in res3.data:
    client.table('trades_log').delete().eq('id', r['id']).execute()

# Desactivar modo de producción
client.table('bot_status').update({'modo_produccion': False}).eq('id', 1).execute()

print("Base de datos de pruebas limpia.")
