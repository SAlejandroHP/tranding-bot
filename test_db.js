import { createClient } from '@supabase/supabase-js';
import dotenv from 'dotenv';
dotenv.config({ path: './saak-dashboard/.env' });

const supabase = createClient(process.env.VITE_SUPABASE_URL, process.env.VITE_SUPABASE_ANON_KEY);

async function check() {
  const { data, error } = await supabase.from('bot_status').select('*').limit(1);
  console.log('Bot Status columns:', data ? Object.keys(data[0]) : error);
}
check();
