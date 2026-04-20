import process
import asyncio
from supabase import create_client

async def main():
    import os
    from dotenv import load_dotenv
    load_dotenv('saak-dashboard/.env')
    
    url = os.getenv('VITE_SUPABASE_URL')
    key = os.getenv('VITE_SUPABASE_ANON_KEY')
    
    if not url or not key:
        print("Credenciales no encontradas")
        return

    # To test updateUser we would need the user's JWT. We can only use Admin role to update raw_user_meta_data directly via the service key.
    # Actually, the user's frontend uses the active session JWT.
    
    # We can at least check if we can connect as admin to see what's wrong.
    # wait, the backend python script uses SUPABASE_URL and SUPABASE_KEY.
    load_dotenv('.env')
    service_key = os.getenv('SUPABASE_KEY')
    
    client = create_client(url, service_key)
    print("Conectado con service key")

    # Let's see the user
    auth_admin = client.auth.admin
    user_res = auth_admin.get_user_by_id('09af4891-bae2-4a92-b823-e550f113285c')
    print("Before:", user_res.user.user_metadata)

    # try updating
    res = auth_admin.update_user_by_id(
        '09af4891-bae2-4a92-b823-e550f113285c',
        user_metadata={'full_name': 'Alejandro SaaK'}
    )
    print("After:", res.user.user_metadata)
    
if __name__ == '__main__':
    asyncio.run(main())
