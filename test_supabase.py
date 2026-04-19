import os
from supabase import create_client

url = os.environ.get("VITE_SUPABASE_URL", "")
key = os.environ.get("VITE_SUPABASE_ANON_KEY", "")

# We need to read from .env if running from cli
from dotenv import load_dotenv
load_dotenv(".env")
url = os.environ.get("VITE_SUPABASE_URL")
key = os.environ.get("VITE_SUPABASE_ANON_KEY")

if url and key:
    supabase = create_client(url, key)
    res = supabase.table("open_positions").select("*").execute()
    print("OPEN POSITIONS:", res.data)
else:
    print("NO ENVS")
