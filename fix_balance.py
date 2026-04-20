import sys
from modulo7_supabase import SupabaseManager
db = SupabaseManager()
db.upsert_bot_status({'id': 1, 'mxn_real_balance': 95.35})
print("Balance fixed.")
