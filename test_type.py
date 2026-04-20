import os
from modulo7_supabase import SupabaseManager
import json
db = SupabaseManager()

try:
    res = db.client.table('bot_status').update({'decision_usuario': json.dumps({'monto_sculp': 500})}).eq('id', 1).execute()
    print("Success")
except Exception as e:
    print("Error:", e)
