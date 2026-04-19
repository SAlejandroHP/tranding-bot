import os
import sys
from dotenv import load_dotenv
from supabase import create_client, Client

class SupabaseManager:
    def __init__(self):
        load_dotenv()
        url: str = os.getenv("SUPABASE_URL")
        key: str = os.getenv("SUPABASE_KEY")
        if not url or not key:
            print("Error: SUPABASE_URL o SUPABASE_KEY no están definidos en el entorno.")
            sys.exit(1)
        self.client: Client = create_client(url, key)

    def select(self, table, limit=None):
        query = self.client.table(table).select('*')
        if limit:
            query = query.limit(limit)
        return query.execute()

    def upsert_bot_status(self, diccionario_estado):
        try:
            return self.client.table('bot_status').upsert(diccionario_estado).execute()
        except Exception as e:
            print(f"Error al hacer upsert en Supabase (bot_status): {e}")

    def get_bot_status(self):
        return self.client.table('bot_status').select('*').eq('id', 1).execute()

    def get_open_positions(self):
        return self.client.table('open_positions').select('*').execute()

    def delete_position(self, pos_id):
        return self.client.table('open_positions').delete().eq('id', pos_id).execute()

    def insert_trade_log(self, data):
        return self.client.table('trades_log').insert(data).execute()

    def insert_position(self, data):
        return self.client.table('open_positions').insert(data).execute()

    def insert_trade_proposal(self, data):
        return self.client.table('trade_proposals').insert(data).execute()

    def get_trade_proposals(self, ids):
        return self.client.table('trade_proposals').select('*').in_('id', ids).execute()

    def update_proposals_status(self, ids, status):
        return self.client.table('trade_proposals').update({'status': status}).in_('id', ids).execute()

    def delete_pending_proposals(self):
        return self.client.table('trade_proposals').delete().in_('status', ['pendiente', 'cancelada', 'rechazada']).execute()
