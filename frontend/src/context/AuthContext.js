import React, { createContext, useState, useContext, useEffect } from 'react';
import axios from 'axios';

const AuthContext = createContext(null);

const API_BASE = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [tokens, setTokens] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const storedUser = localStorage.getItem('health_ai_user');
    const storedTokens = localStorage.getItem('health_ai_tokens');
    if (storedUser && storedTokens) {
      const parsedUser = JSON.parse(storedUser);
      const parsedTokens = JSON.parse(storedTokens);
      setUser(parsedUser);
      setTokens(parsedTokens);
      axios.defaults.headers.common['Authorization'] = `Bearer ${parsedTokens.access}`;
    }
    setLoading(false);
  }, []);

  const login = async (email, password) => {
    const response = await axios.post(`${API_BASE}/auth/login/`, { email, password });
    const { access, refresh, user: userData } = response.data;
    const newTokens = { access, refresh };
    setUser(userData);
    setTokens(newTokens);
    localStorage.setItem('health_ai_user', JSON.stringify(userData));
    localStorage.setItem('health_ai_tokens', JSON.stringify(newTokens));
    axios.defaults.headers.common['Authorization'] = `Bearer ${access}`;
    return userData;
  };

  const register = async (formData) => {
    const response = await axios.post(`${API_BASE}/auth/register/`, formData);
    const { tokens: newTokens, user: userData } = response.data;
    setUser(userData);
    setTokens(newTokens);
    localStorage.setItem('health_ai_user', JSON.stringify(userData));
    localStorage.setItem('health_ai_tokens', JSON.stringify(newTokens));
    axios.defaults.headers.common['Authorization'] = `Bearer ${newTokens.access}`;
    return userData;
  };

  const logout = async () => {
    try {
      if (tokens?.refresh) {
        await axios.post(`${API_BASE}/auth/logout/`, { refresh: tokens.refresh });
      }
    } catch (err) {
      // Token may already be invalid
    } finally {
      setUser(null);
      setTokens(null);
      localStorage.removeItem('health_ai_user');
      localStorage.removeItem('health_ai_tokens');
      delete axios.defaults.headers.common['Authorization'];
    }
  };

  const refreshToken = async () => {
    try {
      const response = await axios.post(`${API_BASE}/auth/token/refresh/`, {
        refresh: tokens?.refresh,
      });
      const newTokens = { ...tokens, access: response.data.access };
      setTokens(newTokens);
      localStorage.setItem('health_ai_tokens', JSON.stringify(newTokens));
      axios.defaults.headers.common['Authorization'] = `Bearer ${response.data.access}`;
      return response.data.access;
    } catch (err) {
      logout();
      throw err;
    }
  };

  return (
    <AuthContext.Provider value={{ user, tokens, loading, login, register, logout, refreshToken }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) throw new Error('useAuth must be used within AuthProvider');
  return context;
};

export default AuthContext;
