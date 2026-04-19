import { supabase } from './supabaseClient';
import { TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID } from '../config/env';

let currentCode = null;

export const authService = {
  sendCode: async (email) => {
    if (email !== 'saakhgpv@gmail.com') {
      return { success: false, error: 'Usuario no autorizado.' };
    }

    currentCode = Math.floor(100000 + Math.random() * 900000).toString();

    try {
      const text = `SaaK Dashboard: Código de acceso: ${currentCode}`;
      const url = `https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage`;
      const response = await fetch(url, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ chat_id: TELEGRAM_CHAT_ID, text: text }),
      });

      if (!response.ok) {
        throw new Error('No se pudo enviar el mensaje a Telegram');
      }

      return { success: true };
    } catch (error) {
      console.error('Error enviando código de Telegram:', error);
      return { success: false, error: error.message };
    }
  },

  verifyCode: async (email, code) => {
    try {
      if (email !== 'saakhgpv@gmail.com') {
         return { success: false, error: 'Usuario no autorizado' };
      }
      if (currentCode === null) {
         return { success: false, error: 'No has solicitado un código' };
      }
      if (code !== currentCode) {
         return { success: false, error: 'Código incorrecto' };
      }

      // Inicio de sesión exitoso (Validado mediante Telegram)
      currentCode = null;
      return { success: true };
    } catch (error) {
      return { success: false, error: error.message };
    }
  },

  logout: async () => {
    currentCode = null;
    return { success: true };
  }
};
