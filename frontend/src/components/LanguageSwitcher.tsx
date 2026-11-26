import { Languages } from "lucide-react";
import { useLanguage } from "@/hooks/useLanguage";
import { SUPPORTED_LANGUAGES } from "@/i18n/types";
import { cn } from "@/utils/cn";

export function LanguageSwitcher({ compact = false }: { compact?: boolean }) {
  const { language, setLanguage } = useLanguage();

  return (
    <div
      className={cn(
        "inline-flex items-center gap-1 rounded-xl border border-blue-200/80 bg-blue-50/70 p-1",
        compact ? "w-full justify-between" : ""
      )}
      role="group"
      aria-label="Language selector"
    >
      <span className="hidden items-center pl-1.5 text-medical-blue sm:inline-flex">
        <Languages className="h-3.5 w-3.5" />
      </span>
      <div className={cn("flex items-center gap-1", compact ? "flex-1 justify-end" : "")}>
        {SUPPORTED_LANGUAGES.map((lang) => {
          const active = language === lang.code;
          return (
            <button
              key={lang.code}
              type="button"
              onClick={() => setLanguage(lang.code)}
              className={cn(
                "rounded-lg px-2 py-1 text-xs font-semibold transition-all",
                active
                  ? "bg-medical-blue text-white shadow-sm"
                  : "text-slate-600 hover:bg-white hover:text-medical-blue"
              )}
              title={lang.label}
            >
              {lang.nativeLabel}
            </button>
          );
        })}
      </div>
    </div>
  );
}
