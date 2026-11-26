import { useEffect, useState } from "react";
import {
  Activity,
  ArrowRight,
  BookOpen,
  FileText,
  FolderHeart,
  Image as ImageIcon,
  Loader2,
  MessageSquareHeart,
  Stethoscope,
  UserCheck,
} from "lucide-react";
import { Link } from "react-router-dom";
import { AiConfigNotice } from "@/components/AiConfigNotice";
import { DisclaimerBanner } from "@/components/DisclaimerBanner";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { useLanguage } from "@/hooks/useLanguage";
import { api } from "@/services/api";
import type { DashboardOverview } from "@/types/api";
import { formatDateTime } from "@/utils/format";

const CATEGORY_TRANSLATIONS: Record<string, Record<string, string>> = {
  "General Health": { en: "General Health", te: "సాధారణ ఆరోగ్యం", hi: "सामान्य स्वास्थ्य" },
  Nutrition: { en: "Nutrition", te: "పోషకాహారం", hi: "पोषण" },
  "Fitness and Exercise": { en: "Fitness and Exercise", te: "ఫిట్‌నెస్ & వ్యాయామం", hi: "फिटनेस और व्यायाम" },
  "Preventive Healthcare": { en: "Preventive Healthcare", te: "నివారణ ఆరోగ్య సంరక్షణ", hi: "निवारक स्वास्थ्य देखभाल" },
  "Common Health Conditions": { en: "Common Health Conditions", te: "సాధారణ ఆరోగ్య సమస్యలు", hi: "सामान्य स्वास्थ्य समस्याएँ" },
  "Mental Wellness": { en: "Mental Wellness", te: "మానసిక ఆరోగ్యం", hi: "मानसिक स्वास्थ्य" },
};

export function DashboardPage() {
  const { language, t } = useLanguage();
  const [data, setData] = useState<DashboardOverview | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api
      .getDashboardOverview()
      .then(setData)
      .catch((err) => setError(err instanceof Error ? err.message : "Failed to load dashboard."))
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <div className="flex min-h-[360px] items-center justify-center">
        <Loader2 className="h-6 w-6 animate-spin text-medical-blue" />
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="rounded-xl border border-red-200 bg-red-50 p-6 text-sm text-red-700">
        {error || "Unable to load dashboard data."}
      </div>
    );
  }

  const statCards = [
    { label: t("dash.statReports"), value: data.stats.total_reports, icon: FileText, to: "/dashboard/reports" },
    { label: t("dash.statSummaries"), value: data.stats.summarized_reports, icon: Activity, to: "/dashboard/reports" },
    { label: t("dash.statChats"), value: data.stats.total_chat_sessions, icon: MessageSquareHeart, to: "/dashboard/chat" },
    { label: t("dash.statSymptoms"), value: data.stats.total_symptom_checks, icon: Stethoscope, to: "/dashboard/symptoms" },
    { label: t("dash.statImages"), value: data.stats.total_images, icon: ImageIcon, to: "/dashboard/images" },
  ];

  const quickServices = [
    { title: t("nav.chat"), desc: t("dash.qChatDesc"), to: "/dashboard/chat", icon: MessageSquareHeart },
    { title: t("nav.symptoms"), desc: t("dash.qSymDesc"), to: "/dashboard/symptoms", icon: Stethoscope },
    { title: t("nav.reports"), desc: t("dash.qRepDesc"), to: "/dashboard/reports", icon: FileText },
    { title: t("nav.images"), desc: t("dash.qImgDesc"), to: "/dashboard/images", icon: ImageIcon },
  ];

  const libraryShortcuts = Object.keys(CATEGORY_TRANSLATIONS);

  return (
    <div className="space-y-6">
      <div className="flex flex-col justify-between gap-4 rounded-2xl bg-gradient-to-r from-medical-blue to-medical-cyan p-6 text-white shadow-soft sm:flex-row sm:items-center">
        <div>
          <p className="text-xs font-semibold uppercase tracking-wider text-blue-100">
            {t("dash.hub")}
          </p>
          <h1 className="mt-1 text-2xl font-bold sm:text-3xl">
            {t("dash.welcome")}, {data.user.full_name}
          </h1>
          <p className="mt-1 text-sm text-blue-50">{t("dash.liveSub")}</p>
        </div>
        <div className="flex flex-wrap items-center gap-2">
          <Badge className="border-white/30 bg-white/15 text-white">
            {data.ai_status.configured
              ? `${t("dash.aiReady")} (${data.ai_status.chat_model})`
              : t("dash.aiNeedsKey")}
          </Badge>
          <Button variant="secondary" asChild>
            <Link to="/dashboard/records">
              <FolderHeart className="h-4 w-4" /> {t("dash.myRecords")}
            </Link>
          </Button>
        </div>
      </div>

      <AiConfigNotice configured={data.ai_status.configured} />
      {data.database_mode === "ephemeral_sqlite" && (
        <div className="rounded-xl border border-amber-300 bg-amber-50 p-4 text-sm text-amber-900">
          <p className="font-semibold">Temporary Serverless Database Active</p>
          <p className="mt-0.5 text-amber-800">
            Connect a PostgreSQL database (Neon Postgres in Vercel Storage or Supabase{" "}
            <code>DATABASE_URL</code>) and redeploy so user logins, reports, and chats persist
            across serverless restarts.
          </p>
        </div>
      )}

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-5">
        {statCards.map((item) => {
          const Icon = item.icon;
          return (
            <Link key={item.label} to={item.to}>
              <Card className="h-full hover:-translate-y-0.5 hover:shadow-soft">
                <CardContent className="flex items-center justify-between p-5">
                  <div>
                    <p className="text-xs font-medium text-slate-500">{item.label}</p>
                    <p className="mt-1 text-2xl font-bold text-slate-900">{item.value}</p>
                  </div>
                  <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-blue-50 text-medical-blue">
                    <Icon className="h-5 w-5" />
                  </div>
                </CardContent>
              </Card>
            </Link>
          );
        })}
      </div>

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {quickServices.map((svc) => {
          const Icon = svc.icon;
          return (
            <Link key={svc.to} to={svc.to}>
              <Card className="h-full border-blue-100 hover:border-medical-blue/50 hover:shadow-soft">
                <CardContent className="flex items-center justify-between p-4">
                  <div className="flex items-center gap-3">
                    <span className="flex h-10 w-10 items-center justify-center rounded-xl bg-cyan-50 text-cyan-700">
                      <Icon className="h-5 w-5" />
                    </span>
                    <div>
                      <p className="text-sm font-semibold text-slate-900">{svc.title}</p>
                      <p className="text-xs text-slate-500">{svc.desc}</p>
                    </div>
                  </div>
                  <ArrowRight className="h-4 w-4 text-slate-400" />
                </CardContent>
              </Card>
            </Link>
          );
        })}
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between">
            <div>
              <CardTitle>{t("dash.recentReports")}</CardTitle>
              <CardDescription>{t("dash.recentReportsSub")}</CardDescription>
            </div>
            <Button variant="ghost" size="sm" asChild>
              <Link to="/dashboard/reports">{t("dash.viewAll")}</Link>
            </Button>
          </CardHeader>
          <CardContent>
            {data.recent_reports.length === 0 ? (
              <p className="text-sm text-slate-500">{t("dash.noReports")}</p>
            ) : (
              <div className="space-y-3">
                {data.recent_reports.map((report) => (
                  <Link
                    key={report.id}
                    to="/dashboard/reports"
                    className="flex items-center justify-between rounded-xl border border-slate-100 p-3 hover:bg-slate-50"
                  >
                    <div className="min-w-0">
                      <p className="truncate text-sm font-medium text-slate-900">
                        {report.original_filename}
                      </p>
                      <p className="text-xs text-slate-500">{formatDateTime(report.created_at)}</p>
                    </div>
                    <Badge variant={report.has_summary ? "success" : "neutral"}>
                      {report.status}
                    </Badge>
                  </Link>
                ))}
              </div>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between">
            <div>
              <CardTitle>{t("dash.recentChats")}</CardTitle>
              <CardDescription>{t("dash.recentChatsSub")}</CardDescription>
            </div>
            <Button variant="ghost" size="sm" asChild>
              <Link to="/dashboard/chat">{t("dash.openChat")}</Link>
            </Button>
          </CardHeader>
          <CardContent>
            {data.recent_chats.length === 0 ? (
              <p className="text-sm text-slate-500">{t("dash.noChats")}</p>
            ) : (
              <div className="space-y-3">
                {data.recent_chats.map((chat) => (
                  <Link
                    key={chat.id}
                    to={`/dashboard/chat?session=${chat.id}`}
                    className="flex items-center justify-between rounded-xl border border-slate-100 p-3 hover:bg-slate-50"
                  >
                    <div className="min-w-0">
                      <p className="truncate text-sm font-medium text-slate-900">{chat.title}</p>
                      <p className="text-xs text-slate-500">{formatDateTime(chat.updated_at)}</p>
                    </div>
                    <Badge>{chat.message_count}</Badge>
                  </Link>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      <div className="grid gap-6 lg:grid-cols-3">
        <Card className="lg:col-span-2">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <BookOpen className="h-5 w-5 text-medical-blue" /> {t("dash.libShortcuts")}
            </CardTitle>
            <CardDescription>{t("dash.libShortcutsSub")}</CardDescription>
          </CardHeader>
          <CardContent className="flex flex-wrap gap-2">
            {libraryShortcuts.map((cat) => (
              <Button key={cat} variant="outline" size="sm" asChild>
                <Link to={`/dashboard/library?category=${encodeURIComponent(cat)}`}>
                  {CATEGORY_TRANSLATIONS[cat]?.[language] || cat}
                </Link>
              </Button>
            ))}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <UserCheck className="h-5 w-5 text-medical-cyan" /> {t("dash.profileSummary")}
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-2 text-sm text-slate-600">
            <p><strong className="text-slate-800">{t("dash.nameLabel")}:</strong> {data.user.full_name}</p>
            <p><strong className="text-slate-800">{t("dash.bloodTypeLabel")}:</strong> {data.user.profile?.blood_type || t("dash.notSet")}</p>
            <p><strong className="text-slate-800">{t("dash.allergiesLabel")}:</strong> {data.user.profile?.allergies || t("dash.noneRecorded")}</p>
            <Button variant="secondary" size="sm" className="mt-2 w-full" asChild>
              <Link to="/dashboard/records">{t("dash.updateProfile")}</Link>
            </Button>
          </CardContent>
        </Card>
      </div>

      <DisclaimerBanner />
    </div>
  );
}
