from modulo7_supabase import SupabaseManager
import time

db = SupabaseManager()
positions = db.get_open_positions().data
for p in positions:
    if p['simbolo'] == 'LTC/MXN':
        print(f"Encontrado {p['id']}, volumen viejo: {p['cantidad']}")
        db.client.table('open_positions').update({'cantidad': 0.09619747}).eq('id', p['id']).execute()
        print("Volumen actualizado al espejo fisico de Bitso.")
