import { AlertTriangle, ShieldAlert } from "lucide-react";
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
          {title ||
            (isEmergency
              ? "Immediate Medical Attention Advised"
              : "Educational Healthcare Information Only")}
        </p>
        <p className="leading-relaxed">
          {message ||
            (isEmergency
              ? "Potential emergency warning signs were detected. Call your local emergency number (e.g., 911 / 112 / 999) or go to the nearest emergency room right away."
              : "This platform provides educational health information only. It does not diagnose conditions, prescribe medication, or replace care from a licensed clinician.")}
        </p>
        {reasons && reasons.length > 0 && (
          <p className="text-xs font-medium text-red-700">
            Detected signals: {reasons.join(" · ")}
          </p>
        )}
      </div>
    </div>
  );
}
