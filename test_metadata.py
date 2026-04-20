import os
import sys
import asyncio
from dotenv import load_dotenv
from supabase import create_client

async def main():
    load_dotenv('.env')
    url = os.getenv('SUPABASE_URL')
    key = os.getenv('SUPABASE_KEY')
    
    if not url or not key:
        print("Error: No hay credenciales.")
        sys.exit(1)

    client = create_client(url, key)
    
    try:
        # User ID known from JSON
        user_id = '09af4891-bae2-4a92-b823-e550f113285c'
        
        # We manually push metadata directly via the admin api to confirm the DB is responsive
        res = client.auth.admin.update_user_by_id(
            user_id,
            user_metadata={'full_name': 'Alejandro SaaK Quantum', 'email_verified': True}
        )
        print("Updated User Metadata via Admin:", res.user.user_metadata)
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())
