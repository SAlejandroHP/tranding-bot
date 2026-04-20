import { useState, useCallback, useEffect } from 'react';
import { authService } from '../services/authService';
import { supabase } from '../services/supabaseClient';

export const useAuth = () => {
  const [isLogged, setIsLogged] = useState(false);
  const [loading, setLoading] = useState(false);
  const [isInitializing, setIsInitializing] = useState(true);
  const [error, setError] = useState(null);
  const [step, setStep] = useState(1);

  useEffect(() => {
    const checkSession = async () => {
      try {
        const { data: { session } } = await supabase.auth.getSession();
        if (session) {
          setIsLogged(true);
        }
      } catch (err) {
        console.error("No se pudo obtener la sesión previa", err);
      } finally {
        setIsInitializing(false);
      }
    };
    checkSession();

    const { data: authListener } = supabase.auth.onAuthStateChange((event, session) => {
      if (session) {
        setIsLogged(true);
      } else {
        setIsLogged(false);
      }
    });

    return () => {
      authListener?.subscription.unsubscribe();
    };
  }, []);

  const requestLoginCode = useCallback(async (email) => {
    setLoading(true);
    setError(null);
    try {
      const response = await authService.sendCode(email);
      if (response.success) {
        setStep(2);
      } else {
        setError(response.error);
      }
    } catch (err) {
      setError(err.message || 'Error inesperado solicitando código');
    } finally {
      setLoading(false);
    }
  }, []);

  const verifyLoginCode = useCallback(async (email, code) => {
    setLoading(true);
    setError(null);
    try {
      const response = await authService.verifyCode(email, code);
      if (response.success) {
        setIsLogged(true); // The auth listener will also catch this
      } else {
        setError(response.error || 'Código incorrecto');
      }
    } catch (err) {
      setError(err.message || 'Error inesperado verificando código');
    } finally {
      setLoading(false);
    }
  }, []);

  const logout = useCallback(async () => {
    setLoading(true);
    await authService.logout();
    setIsLogged(false);
    setStep(1);
    setLoading(false);
    // Reload shouldn't be strictly necessary if state is managed, but kept for safe reset
    window.location.reload(); 
  }, []);

  return { isLogged, step, requestLoginCode, verifyLoginCode, logout, loading, error, isInitializing };
};
