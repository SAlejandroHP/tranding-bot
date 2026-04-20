import os
from modulo7_supabase import SupabaseManager
db = SupabaseManager()
res = db.client.table('bot_status').select('*').limit(1).execute()
print(res.data[0].keys())
