/* eslint-disable react-refresh/only-export-components */
/**
 * Auth context – stores user state in React context.
 * Access token lives in memory only (not localStorage).
 */
import { createContext, useContext, useState, useEffect, type ReactNode } from 'react';
import api, { setAccessToken } from '../services/api';

interface User {
  id: number;
  name: string;
  email: string;
}

interface AuthContextType {
  user: User | null;
  isLoading: boolean;
  login: (email: string, password: string) => Promise<void>;
  signup: (name: string, email: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  // Try to restore session on mount via refresh token cookie
  useEffect(() => {
    const restore = async () => {
      try {
        const { data } = await api.post('/auth/refresh');
        setAccessToken(data.access_token);
        const me = await api.get('/auth/me');
        setUser(me.data);
      } catch {
        setAccessToken(null);
        setUser(null);
      } finally {
        setIsLoading(false);
      }
    };
    restore();
  }, []);

  const login = async (email: string, password: string) => {
    const { data } = await api.post('/auth/login', { email, password });
    setAccessToken(data.access_token);
    const me = await api.get('/auth/me');
    setUser(me.data);
  };

  const signup = async (name: string, email: string, password: string) => {
    const { data } = await api.post('/auth/signup', { name, email, password });
    setAccessToken(data.access_token);
    const me = await api.get('/auth/me');
    setUser(me.data);
  };

  const logout = async () => {
    try {
      await api.post('/auth/logout');
    } catch { /* ignore */ }
    setAccessToken(null);
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, isLoading, login, signup, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used within AuthProvider');
  return ctx;
}
