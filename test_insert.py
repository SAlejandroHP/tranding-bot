import os
from modulo7_supabase import SupabaseManager
db = SupabaseManager()
try:
    res = db.client.table('bot_status').update({'monto_operativo': 500}).eq('id', 1).execute()
    print("Success")
except Exception as e:
    print("Error:", e)
