import { createContext, useContext, useEffect, useState } from 'react';
import api from './api';

const AuthContext = createContext(null);
export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  useEffect(() => {
    if (!sessionStorage.getItem('hair_token')) { setLoading(false); return; }
    api.get('/auth/me').then(({ data }) => setUser(data.user)).catch(() => {
      sessionStorage.removeItem('hair_token');
    }).finally(() => setLoading(false));
  }, []);
  const login = async (email, password) => {
    const { data } = await api.post('/auth/login', { email, password });
    sessionStorage.setItem('hair_token', data.token);
    setUser(data.user);
  };
  const logout = async () => {
    try { await api.post('/auth/logout'); } catch { /* cerrar sesión igualmente en el navegador */ }
    sessionStorage.removeItem('hair_token');
    setUser(null);
  };
  return <AuthContext.Provider value={{ user, loading, login, logout }}>{children}</AuthContext.Provider>;
}
export function useAuth() {
  const value = useContext(AuthContext);
  if (!value) throw new Error('useAuth requiere AuthProvider');
  return value;
}
