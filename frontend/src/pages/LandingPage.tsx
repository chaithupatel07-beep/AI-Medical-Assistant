import {
  ArrowRight,
  BookOpen,
  CheckCircle2,
  FileText,
  FolderHeart,
  Image as ImageIcon,
  Lock,
  MessageSquareHeart,
  ShieldCheck,
  Sparkles,
  Stethoscope,
} from "lucide-react";
import { Link } from "react-router-dom";
import { HeroIllustration } from "@/assets/HeroIllustration";
import { DisclaimerBanner } from "@/components/DisclaimerBanner";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { useLanguage } from "@/hooks/useLanguage";

export function LandingPage() {
  const { t } = useLanguage();

  const features = [
    { icon: MessageSquareHeart, title: t("landing.f1.title"), description: t("landing.f1.desc") },
    { icon: FileText, title: t("landing.f2.title"), description: t("landing.f2.desc") },
    { icon: Stethoscope, title: t("landing.f3.title"), description: t("landing.f3.desc") },
    { icon: ImageIcon, title: t("landing.f4.title"), description: t("landing.f4.desc") },
    { icon: BookOpen, title: t("landing.f5.title"), description: t("landing.f5.desc") },
    { icon: FolderHeart, title: t("landing.f6.title"), description: t("landing.f6.desc") },
  ];

  const steps = [
    { num: "01", title: t("landing.s1.title"), text: t("landing.s1.desc") },
    { num: "02", title: t("landing.s2.title"), text: t("landing.s2.desc") },
    { num: "03", title: t("landing.s3.title"), text: t("landing.s3.desc") },
    { num: "04", title: t("landing.s4.title"), text: t("landing.s4.desc") },
  ];

  const benefits = [t("landing.b1"), t("landing.b2"), t("landing.b3"), t("landing.b4")];

  return (
    <div className="space-y-20 pb-16">
      <section className="relative overflow-hidden bg-gradient-to-b from-blue-50/90 via-sky-50/40 to-transparent pt-12 pb-16 lg:pt-20">
        <div className="mx-auto grid max-w-7xl items-center gap-12 px-4 sm:px-6 lg:grid-cols-2 lg:px-8">
          <div className="space-y-6">
            <Badge className="gap-1.5 px-3 py-1 text-xs">
              <Sparkles className="h-3.5 w-3.5" />
              {t("landing.badge")}
            </Badge>
            <h1 className="text-4xl font-extrabold tracking-tight text-slate-900 sm:text-5xl lg:text-6xl">
              {t("landing.heroTitleStart")}{" "}
              <span className="bg-gradient-to-r from-medical-blue to-medical-cyan bg-clip-text text-transparent">
                {t("landing.heroTitleAccent")}
              </span>
            </h1>
            <p className="max-w-xl text-base leading-relaxed text-slate-600 sm:text-lg">
              {t("landing.heroSubtitle")}
            </p>
            <div className="flex flex-wrap items-center gap-3">
              <Button size="lg" asChild>
                <Link to="/register">
                  {t("nav.getStarted")} <ArrowRight className="h-4 w-4" />
                </Link>
              </Button>
              <Button size="lg" variant="outline" asChild>
                <a href="#features">{t("landing.exploreServices")}</a>
              </Button>
            </div>
            <div className="flex flex-wrap items-center gap-6 pt-2 text-xs font-medium text-slate-500">
              <span className="inline-flex items-center gap-1.5">
                <Lock className="h-4 w-4 text-medical-blue" /> {t("landing.privateRecords")}
              </span>
              <span className="inline-flex items-center gap-1.5">
                <ShieldCheck className="h-4 w-4 text-medical-cyan" /> {t("landing.nonDiagnostic")}
              </span>
            </div>
          </div>

          <HeroIllustration />
        </div>
      </section>

      <section id="features" className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div className="mx-auto max-w-2xl text-center">
          <Badge variant="cyan">{t("landing.modulesBadge")}</Badge>
          <h2 className="mt-3 text-3xl font-bold tracking-tight text-slate-900 sm:text-4xl">
            {t("landing.modulesTitle")}
          </h2>
          <p className="mt-3 text-slate-600">{t("landing.modulesSub")}</p>
        </div>

        <div className="mt-10 grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
          {features.map((f) => {
            const Icon = f.icon;
            return (
              <Card key={f.title} className="group hover:-translate-y-0.5 hover:shadow-soft">
                <CardHeader>
                  <div className="mb-2 flex h-11 w-11 items-center justify-center rounded-xl bg-blue-50 text-medical-blue transition-colors group-hover:bg-medical-blue group-hover:text-white">
                    <Icon className="h-5 w-5" />
                  </div>
                  <CardTitle>{f.title}</CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-sm leading-relaxed text-slate-600">{f.description}</p>
                </CardContent>
              </Card>
            );
          })}
        </div>
      </section>

      <section id="how-it-works" className="border-y border-blue-100 bg-white/80 py-16">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="mx-auto max-w-2xl text-center">
            <Badge>{t("landing.workflowBadge")}</Badge>
            <h2 className="mt-3 text-3xl font-bold tracking-tight text-slate-900">
              {t("landing.workflowTitle")}
            </h2>
          </div>

          <div className="mt-10 grid gap-6 sm:grid-cols-2 lg:grid-cols-4">
            {steps.map((s) => (
              <div
                key={s.num}
                className="rounded-2xl border border-blue-100 bg-gradient-to-b from-white to-blue-50/40 p-6 shadow-card"
              >
                <span className="text-2xl font-extrabold text-medical-cyan">{s.num}</span>
                <h3 className="mt-3 text-base font-bold text-slate-900">{s.title}</h3>
                <p className="mt-2 text-sm leading-relaxed text-slate-600">{s.text}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      <section className="mx-auto grid max-w-7xl items-center gap-10 px-4 sm:px-6 lg:grid-cols-2 lg:px-8">
        <div className="space-y-5">
          <Badge variant="success">{t("landing.whyBadge")}</Badge>
          <h2 className="text-3xl font-bold tracking-tight text-slate-900">
            {t("landing.whyTitle")}
          </h2>
          <p className="text-slate-600">{t("landing.whySub")}</p>
          <ul className="space-y-3">
            {benefits.map((b) => (
              <li key={b} className="flex items-start gap-2.5 text-sm text-slate-700">
                <CheckCircle2 className="mt-0.5 h-5 w-5 shrink-0 text-medical-cyan" />
                <span>{b}</span>
              </li>
            ))}
          </ul>
          <Button asChild>
            <Link to="/library">{t("landing.browseLib")}</Link>
          </Button>
        </div>

        <Card id="safety" className="border-blue-200 bg-gradient-to-br from-white to-blue-50/60 p-6">
          <div className="space-y-4">
            <h3 className="text-xl font-bold text-slate-900">{t("landing.safetyCardTitle")}</h3>
            <DisclaimerBanner />
            <p className="text-sm leading-relaxed text-slate-600">{t("landing.safetyCardDesc")}</p>
          </div>
        </Card>
      </section>
    </div>
  );
}
