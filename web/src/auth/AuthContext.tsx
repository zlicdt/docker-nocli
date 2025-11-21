import React, { createContext, useContext, useEffect, useMemo, useState } from "react";

import { fetchAuthStatus, login, setupAdmin } from "./api";
import type { LoginResponse } from "./api";

type AuthStatus = "loading" | "setup" | "unauthenticated" | "authenticated";

type AuthContextValue = {
  status: AuthStatus;
  token: string | null;
  loginWithPassword: (username: string, password: string) => Promise<void>;
  setupAndLogin: (username: string, password: string) => Promise<void>;
  logout: () => void;
};

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

const TOKEN_KEY = "docker-nocli-auth-token";

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [status, setStatus] = useState<AuthStatus>("loading");
  const [token, setToken] = useState<string | null>(null);

  useEffect(() => {
    const init = async () => {
      try {
        const statusRes = await fetchAuthStatus();
        if (statusRes.setup_required) {
          setStatus("setup");
          setToken(null);
          localStorage.removeItem(TOKEN_KEY);
          return;
        }

        const storedToken = localStorage.getItem(TOKEN_KEY);
        if (storedToken) {
          setToken(storedToken);
          setStatus("authenticated");
          return;
        }

        setStatus("unauthenticated");
      } catch (error) {
        console.error("Failed to initialize auth", error);
        setStatus("unauthenticated");
      }
    };

    void init();
  }, []);

  const persistToken = (value: string) => {
    localStorage.setItem(TOKEN_KEY, value);
    setToken(value);
  };

  const loginWithPassword = async (username: string, password: string) => {
    const res: LoginResponse = await login(username, password);
    persistToken(res.token);
    setStatus("authenticated");
  };

  const setupAndLogin = async (username: string, password: string) => {
    await setupAdmin(username, password);
    await loginWithPassword(username, password);
  };

  const logout = () => {
    localStorage.removeItem(TOKEN_KEY);
    setToken(null);
    setStatus("unauthenticated");
  };

  const value = useMemo<AuthContextValue>(
    () => ({
      status,
      token,
      loginWithPassword,
      setupAndLogin,
      logout,
    }),
    [status, token],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext);
  if (!ctx) {
    throw new Error("useAuth must be used within AuthProvider");
  }
  return ctx;
}
