import React, { createContext, useCallback, useContext, useEffect, useState } from "react";
import {
  api,
  ApiError,
  AUTH_EXPIRED_EVENT,
  getAuthToken,
  getCachedUser,
  setAuthToken,
  setCachedUser,
} from "@/services/api";
import type { User } from "@/types/api";

interface AuthContextValue {
  user: User | null;
  loading: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (fullName: string, email: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
  refreshUser: () => Promise<void>;
  setUserDirect: (user: User) => void;
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined);
const TOKEN_REFRESH_INTERVAL_MS = 30 * 60 * 1000;

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(() => (getAuthToken() ? getCachedUser() : null));
  const [loading, setLoading] = useState<boolean>(() => Boolean(getAuthToken() && !getCachedUser()));

  const updateUserState = useCallback((nextUser: User | null) => {
    setCachedUser(nextUser);
    setUser(nextUser);
  }, []);

  const refreshUser = useCallback(async () => {
    const token = getAuthToken();
    if (!token) {
      updateUserState(null);
      setLoading(false);
      return;
    }
    try {
      const current = await api.me();
      updateUserState(current);
    } catch (err) {
      // Only clear session when the backend explicitly rejects credentials (401);
      // preserve session across network hiccups, 5xx cold starts, or tab sleep.
      if (err instanceof ApiError && err.status === 401) {
        setAuthToken(null);
        updateUserState(null);
      }
    } finally {
      setLoading(false);
    }
  }, [updateUserState]);

  useEffect(() => {
    void refreshUser();
  }, [refreshUser]);

  useEffect(() => {
    const onExpired = () => {
      setAuthToken(null);
      updateUserState(null);
    };
    const onStorage = (event: StorageEvent) => {
      if (event.key === "ai_med_assistant_token" && !event.newValue) {
        updateUserState(null);
      } else if (event.key === "ai_med_assistant_token" && event.newValue) {
        void refreshUser();
      }
    };
    const onVisibility = () => {
      if (document.visibilityState === "visible" && getAuthToken()) {
        void refreshUser();
      }
    };

    window.addEventListener(AUTH_EXPIRED_EVENT, onExpired);
    window.addEventListener("storage", onStorage);
    document.addEventListener("visibilitychange", onVisibility);

    const timer = window.setInterval(() => {
      if (getAuthToken()) {
        api
          .refreshToken()
          .then((res) => {
            setAuthToken(res.access_token);
            updateUserState(res.user);
          })
          .catch(() => {
            // Keep existing valid token if transient network failure occurs
          });
      }
    }, TOKEN_REFRESH_INTERVAL_MS);

    return () => {
      window.removeEventListener(AUTH_EXPIRED_EVENT, onExpired);
      window.removeEventListener("storage", onStorage);
      document.removeEventListener("visibilitychange", onVisibility);
      window.clearInterval(timer);
    };
  }, [refreshUser, updateUserState]);

  const login = async (email: string, password: string) => {
    const res = await api.login({ email, password });
    setAuthToken(res.access_token);
    updateUserState(res.user);
    setLoading(false);
  };

  const register = async (fullName: string, email: string, password: string) => {
    const res = await api.register({ full_name: fullName, email, password });
    setAuthToken(res.access_token);
    updateUserState(res.user);
    setLoading(false);
  };

  const logout = async () => {
    try {
      if (getAuthToken()) {
        await api.logout();
      }
    } catch {
      // Clear local session cleanly even if server call fails
    } finally {
      setAuthToken(null);
      updateUserState(null);
    }
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        loading,
        login,
        register,
        logout,
        refreshUser,
        setUserDirect: updateUserState,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext);
  if (!ctx) {
    throw new Error("useAuth must be used within AuthProvider");
  }
  return ctx;
}
