import sys
from modulo7_supabase import SupabaseManager

db = SupabaseManager()
res = db.get_bot_status()
print(res.data)
