import { useState, useCallback } from 'react';
import { authService } from '../services/authService';

export const useAuth = () => {
  const [isLogged, setIsLogged] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [step, setStep] = useState(1);

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
        setIsLogged(true);
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
    window.location.reload();
  }, []);

  return { isLogged, step, requestLoginCode, verifyLoginCode, logout, loading, error };
};
