import { Activity } from "lucide-react";
import { Link } from "react-router-dom";
import { useLanguage } from "@/hooks/useLanguage";

interface BrandLogoProps {
  to?: string;
  compact?: boolean;
}

export function BrandLogo({ to = "/", compact = false }: BrandLogoProps) {
  const { t } = useLanguage();
  return (
    <Link to={to} className="inline-flex items-center gap-2.5 group">
      <span className="flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-br from-medical-blue to-medical-cyan text-white shadow-sm transition-transform group-hover:scale-105">
        <Activity className="h-5 w-5" />
      </span>
      <span className="flex flex-col leading-none">
        <span className="text-base font-bold tracking-tight text-slate-900">
          {t("brand.name")}
        </span>
        {!compact && (
          <span className="text-[11px] font-medium text-cyan-700">
            {t("brand.tagline")}
          </span>
        )}
      </span>
    </Link>
  );
}
