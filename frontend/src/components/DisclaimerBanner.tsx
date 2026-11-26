import { AlertTriangle, ShieldAlert } from "lucide-react";
import { useLanguage } from "@/hooks/useLanguage";
import { cn } from "@/utils/cn";

interface DisclaimerBannerProps {
  variant?: "educational" | "emergency";
  title?: string;
  message?: string;
  reasons?: string[];
  className?: string;
}

export function DisclaimerBanner({
  variant = "educational",
  title,
  message,
  reasons,
  className,
}: DisclaimerBannerProps) {
  const { t } = useLanguage();
  const isEmergency = variant === "emergency";
  return (
    <div
      className={cn(
        "flex items-start gap-3 rounded-xl border p-4 text-sm",
        isEmergency
          ? "border-red-300 bg-red-50 text-red-900"
          : "border-blue-200 bg-blue-50/80 text-slate-700",
        className
      )}
      role="status"
    >
      {isEmergency ? (
        <AlertTriangle className="mt-0.5 h-5 w-5 shrink-0 text-red-600" />
      ) : (
        <ShieldAlert className="mt-0.5 h-5 w-5 shrink-0 text-medical-blue" />
      )}
      <div className="space-y-1">
        <p className={cn("font-semibold", isEmergency ? "text-red-800" : "text-slate-900")}>
          {title || (isEmergency ? t("disclaimer.emergTitle") : t("disclaimer.eduTitle"))}
        </p>
        <p className="leading-relaxed">
          {message || (isEmergency ? t("disclaimer.emergBody") : t("disclaimer.eduBody"))}
        </p>
        {reasons && reasons.length > 0 && (
          <p className="text-xs font-medium text-red-700">
            {t("disclaimer.detectedSignals")}: {reasons.join(" · ")}
          </p>
        )}
      </div>
    </div>
  );
}
