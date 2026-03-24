import { createContext, useContext, useState, useEffect, useCallback } from "react";
import { authApi } from "../services/api";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  const loadUser = useCallback(async () => {
    const token = localStorage.getItem("token");
    if (!token) {
      setLoading(false);
      return;
    }
    try {
      const res = await authApi.me();
      setUser(res.data);
    } catch {
      localStorage.removeItem("token");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadUser();
  }, [loadUser]);

  const login = async (username, password) => {
    const res = await authApi.login({ username, password });
    localStorage.setItem("token", res.data.access_token);
    await loadUser();
  };

  const logout = () => {
    localStorage.removeItem("token");
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, loading, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export const useAuth = () => useContext(AuthContext);
