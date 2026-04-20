import { supabase } from './supabaseClient';
import { TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID } from '../config/env';

export const authService = {
  sendCode: async (email) => {
    try {
      const { error } = await supabase.auth.signInWithOtp({
        email: email,
        options: {
          shouldCreateUser: true,
          emailRedirectTo: window.location.origin
        }
      });
      if (error) {
        return { success: false, error: error.message };
      }
      return { success: true };
    } catch (error) {
      console.error('Error enviando código con Supabase:', error);
      return { success: false, error: error.message };
    }
  },

  verifyCode: async (email, code) => {
    try {
      const { data, error } = await supabase.auth.verifyOtp({
        email,
        token: code,
        type: 'email'
      });
      
      if (error) {
        return { success: false, error: error.message };
      }
      
      if (data?.session) {
        return { success: true };
      }
      return { success: false, error: 'Sesión no pudo ser establecida' };
    } catch (error) {
      return { success: false, error: error.message };
    }
  },

  logout: async () => {
    try {
      await supabase.auth.signOut();
    } catch (e) {
      console.warn("Error en signOut del servidor:", e);
    }
    // Fuerza limpieza total local para evitar loops de sesiones fantasmas
    for (let i = 0; i < localStorage.length; i++) {
       const key = localStorage.key(i);
       if (key && key.startsWith('sb-')) {
          localStorage.removeItem(key);
       }
    }
    // O simplemente todo local storage
    localStorage.clear();
    return { success: true };
  }
};
