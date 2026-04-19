import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv(".env")
url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")

supabase = create_client(url, key)
res = supabase.table("bot_status").select("*").execute()
print("BOT STATUS:", res.data)
