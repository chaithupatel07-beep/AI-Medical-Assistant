import React, { createContext, useCallback, useContext, useEffect, useState } from "react";
import { useAuth } from "@/hooks/useAuth";
import { TRANSLATIONS } from "@/i18n/translations";
import { LanguageCode, normalizeLanguage } from "@/i18n/types";
import { api } from "@/services/api";

const LANG_STORAGE_KEY = "ai_med_assistant_lang";

interface LanguageContextValue {
  language: LanguageCode;
  setLanguage: (lang: LanguageCode) => void;
  t: (key: string) => string;
}

const LanguageContext = createContext<LanguageContextValue | undefined>(undefined);

export function LanguageProvider({ children }: { children: React.ReactNode }) {
  const { user, setUserDirect } = useAuth();
  const [language, setLanguageState] = useState<LanguageCode>(() =>
    normalizeLanguage(localStorage.getItem(LANG_STORAGE_KEY))
  );

  useEffect(() => {
    const profileLang = user?.profile?.preferred_language;
    if (profileLang) {
      const normalized = normalizeLanguage(profileLang);
      setLanguageState(normalized);
      localStorage.setItem(LANG_STORAGE_KEY, normalized);
    }
  }, [user?.profile?.preferred_language]);

  useEffect(() => {
    document.documentElement.lang = language;
  }, [language]);

  const setLanguage = useCallback(
    (nextLang: LanguageCode) => {
      const normalized = normalizeLanguage(nextLang);
      setLanguageState(normalized);
      localStorage.setItem(LANG_STORAGE_KEY, normalized);
      if (user) {
        api
          .updateProfile({ preferred_language: normalized })
          .then(setUserDirect)
          .catch(() => {
            // keep local preference even if offline
          });
      }
    },
    [user, setUserDirect]
  );

  const t = useCallback(
    (key: string): string => {
      return TRANSLATIONS[language][key] ?? TRANSLATIONS.en[key] ?? key;
    },
    [language]
  );

  return (
    <LanguageContext.Provider value={{ language, setLanguage, t }}>
      {children}
    </LanguageContext.Provider>
  );
}

export function useLanguage(): LanguageContextValue {
  const ctx = useContext(LanguageContext);
  if (!ctx) {
    throw new Error("useLanguage must be used within LanguageProvider");
  }
  return ctx;
}
