import i18n from "i18next";
import { initReactI18next } from "react-i18next";
import { TRANSLATIONS } from "@/i18n/translations";

if (!i18n.isInitialized) {
  void i18n.use(initReactI18next).init({
    resources: {
      en: { translation: TRANSLATIONS.en },
      te: { translation: TRANSLATIONS.te },
      hi: { translation: TRANSLATIONS.hi },
    },
    lng: "en",
    fallbackLng: "en",
    interpolation: {
      escapeValue: false,
    },
  });
}

export default i18n;
