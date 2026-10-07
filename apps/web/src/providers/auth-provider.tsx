"use client";

import { createContext, useContext, useEffect, useState } from "react";
import { User } from "@/types";
import { isAuthenticated, removeToken, refreshToken } from "@/lib/auth";
import api from "@/lib/api";

interface AuthContextType {
  user: User | null;
  isLoading: boolean;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType>({
  user: null,
  isLoading: true,
  logout: () => {},
});

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchUser = async () => {
      if (isAuthenticated()) {
        try {
          const { data } = await api.get("/auth/me");
          setUser(data);
        } catch (error) {
          try {
            await refreshToken();
            const { data } = await api.get('/auth/me');
            setUser(data);
          } catch { removeToken(); }
        }
      }
      setIsLoading(false);
    };
    fetchUser();
  }, []);

  const logout = async () => {
    try { await api.post('/auth/logout'); } finally {
      removeToken();
      setUser(null);
      window.location.href = '/login';
    }
  };

  return (
    <AuthContext.Provider value={{ user, isLoading, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export const useAuthContext = () => useContext(AuthContext);
