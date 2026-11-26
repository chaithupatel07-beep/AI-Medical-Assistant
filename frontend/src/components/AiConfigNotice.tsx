import { Cpu } from "lucide-react";
import { useLanguage } from "@/hooks/useLanguage";
import type { AiMode } from "@/types/api";

interface AiConfigNoticeProps {
  configured: boolean;
  mode?: AiMode;
}

export function AiConfigNotice({ configured, mode }: AiConfigNoticeProps) {
  const { t } = useLanguage();
  if (configured || mode === "cloud_ai" || mode === "ollama_local") {
    return null;
  }

  return (
    <div className="flex items-start gap-3 rounded-xl border border-blue-200 bg-blue-50/90 p-4 text-sm text-blue-950 dark:border-blue-800/80 dark:bg-blue-950/40 dark:text-blue-100">
      <Cpu className="mt-0.5 h-5 w-5 shrink-0 text-medical-blue dark:text-cyan-400" />
      <div>
        <p className="font-semibold">{t("aiNotice.title")}</p>
        <p className="mt-0.5 text-blue-800 dark:text-blue-200/90">{t("aiNotice.body")}</p>
      </div>
    </div>
  );
}
