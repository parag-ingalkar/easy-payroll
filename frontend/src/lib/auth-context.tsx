"use client";

import * as React from "react";
import { apiFetch } from "@/lib/api";
import { setToken, clearToken } from "@/lib/token-store";
import type { BusinessShape, SessionShape } from "@/lib/types";

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

type AuthState = {
  user: SessionShape | null;
  business: BusinessShape | null;
  loading: boolean;
  refreshUser: () => Promise<void>;
  login: (email: string, password: string) => Promise<void>;
  register: (name: string, email: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
};

const AuthContext = React.createContext<AuthState | null>(null);

// ---------------------------------------------------------------------------
// Provider
// ---------------------------------------------------------------------------

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = React.useState<SessionShape | null>(null);
  const [business, setBusiness] = React.useState<BusinessShape | null>(null);
  const [loading, setLoading] = React.useState(true);

  /** Fetch the current user from the backend and, if authenticated, their business. */
  const refreshUser = React.useCallback(async () => {
    try {
      // Try silent refresh first (cookie-based — works across reloads)
      const tokenData = await apiFetch<{ accessToken: string }>(
        "/api/auth/refresh",
        { method: "POST", body: JSON.stringify({}) },
      );
      if (tokenData.accessToken) {
        setToken(tokenData.accessToken);
      }
    } catch {
      // Refresh failed — not logged in, that's fine
      setUser(null);
      setBusiness(null);
      setLoading(false);
      return;
    }

    try {
      const me = await apiFetch<SessionShape>("/api/users/me");
      setUser(me);

      // Fetch the user's business (owner always has at most one in our flow)
      try {
        const businesses = await apiFetch<BusinessShape[]>("/api/business");
        setBusiness(businesses[0] ?? null);
      } catch {
        setBusiness(null);
      }
    } catch {
      clearToken();
      setUser(null);
      setBusiness(null);
    } finally {
      setLoading(false);
    }
  }, []);

  React.useEffect(() => {
    refreshUser();
  }, [refreshUser]);

  const login = React.useCallback(
    async (email: string, password: string) => {
      const tokenData = await apiFetch<{ accessToken: string }>(
        "/api/auth/login",
        { method: "POST", body: JSON.stringify({ email, password }) },
      );
      setToken(tokenData.accessToken);

      // Hydrate user + business
      const me = await apiFetch<SessionShape>("/api/users/me");
      setUser(me);

      try {
        const businesses = await apiFetch<BusinessShape[]>("/api/business");
        setBusiness(businesses[0] ?? null);
      } catch {
        setBusiness(null);
      }
    },
    [],
  );

  const register = React.useCallback(
    async (name: string, email: string, password: string) => {
      await apiFetch<SessionShape>("/api/auth/register", {
        method: "POST",
        body: JSON.stringify({ name, email, password }),
      });
      // Auto-login after registration
      await login(email, password);
    },
    [login],
  );

  const logout = React.useCallback(async () => {
    try {
      await apiFetch<null>("/api/auth/logout", { method: "POST" });
    } catch {
      // Best-effort — clear local state regardless
    }
    clearToken();
    setUser(null);
    setBusiness(null);
  }, []);

  const value: AuthState = {
    user,
    business,
    loading,
    refreshUser,
    login,
    register,
    logout,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

// ---------------------------------------------------------------------------
// Hook
// ---------------------------------------------------------------------------

export function useAuth() {
  const ctx = React.useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}
