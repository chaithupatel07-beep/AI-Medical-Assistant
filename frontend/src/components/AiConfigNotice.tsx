import { KeyRound } from "lucide-react";
import { useLanguage } from "@/hooks/useLanguage";

export function AiConfigNotice({ configured }: { configured: boolean }) {
  const { t } = useLanguage();
  if (configured) return null;
  return (
    <div className="flex items-start gap-3 rounded-xl border border-amber-300 bg-amber-50 p-4 text-sm text-amber-900">
      <KeyRound className="mt-0.5 h-5 w-5 shrink-0 text-amber-700" />
      <div>
        <p className="font-semibold">{t("aiNotice.title")}</p>
        <p className="mt-0.5 text-amber-800">{t("aiNotice.body")}</p>
      </div>
    </div>
  );
}
