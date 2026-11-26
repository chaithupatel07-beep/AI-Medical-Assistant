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

const features = [
  {
    icon: MessageSquareHeart,
    title: "AI Medical Chatbot",
    description:
      "Ask health questions in plain language and receive educational answers, medical term explanations, and emergency warning checks.",
  },
  {
    icon: FileText,
    title: "Medical Report Summarizer",
    description:
      "Upload PDF, JPG, or PNG lab reports to extract measured values, view supplied reference ranges, and generate plain-English summaries.",
  },
  {
    icon: Stethoscope,
    title: "Symptom Information Checker",
    description:
      "Enter symptom details, duration, and severity to review educational possibilities, red flags, and questions for your doctor.",
  },
  {
    icon: ImageIcon,
    title: "Medical Image Analysis",
    description:
      "Securely send medical-related images to a Vision AI service for high-level visual observations and clear clinical review guidance.",
  },
  {
    icon: BookOpen,
    title: "Health Information Library",
    description:
      "Explore curated articles across 6 health categories linked directly to MedlinePlus, WHO, and CDC resources.",
  },
  {
    icon: FolderHeart,
    title: "Personal Health Dashboard",
    description:
      "Keep your reports, AI summaries, conversations, and health profile private, organized, and downloadable anytime.",
  },
];

const steps = [
  {
    num: "01",
    title: "Create Your Private Account",
    text: "Sign up securely with encrypted credentials so your reports and conversations remain strictly yours.",
  },
  {
    num: "02",
    title: "Upload Reports or Ask Questions",
    text: "Submit lab PDFs/images, describe symptoms, or start a chat with AI Medical Assistant.",
  },
  {
    num: "03",
    title: "Review Clear Educational Insights",
    text: "See extracted values, plain-English explanations, limitations, and safety warnings in seconds.",
  },
  {
    num: "04",
    title: "Prepare for Your Doctor Visit",
    text: "Download your report summary and tailored questions to have more informed clinical conversations.",
  },
];

const benefits = [
  "Translates complex medical jargon into approachable English",
  "Never invents laboratory reference ranges or fake test results",
  "Built-in emergency keyword detection for urgent symptoms",
  "Private user-isolated storage with full record deletion control",
];

export function LandingPage() {
  return (
    <div className="space-y-20 pb-16">
      <section className="relative overflow-hidden bg-gradient-to-b from-blue-50/90 via-sky-50/40 to-transparent pt-12 pb-16 lg:pt-20">
        <div className="mx-auto grid max-w-7xl items-center gap-12 px-4 sm:px-6 lg:grid-cols-2 lg:px-8">
          <div className="space-y-6">
            <Badge className="gap-1.5 px-3 py-1 text-xs">
              <Sparkles className="h-3.5 w-3.5" />
              Educational AI Healthcare Platform
            </Badge>
            <h1 className="text-4xl font-extrabold tracking-tight text-slate-900 sm:text-5xl lg:text-6xl">
              Your Health,{" "}
              <span className="bg-gradient-to-r from-medical-blue to-medical-cyan bg-clip-text text-transparent">
                Smarter with AI
              </span>
            </h1>
            <p className="max-w-xl text-base leading-relaxed text-slate-600 sm:text-lg">
              Understand lab reports, learn about symptoms, explore trusted clinical resources, and
              prepare thoughtful questions before your next healthcare appointment—safely and
              privately.
            </p>
            <div className="flex flex-wrap items-center gap-3">
              <Button size="lg" asChild>
                <Link to="/register">
                  Get Started <ArrowRight className="h-4 w-4" />
                </Link>
              </Button>
              <Button size="lg" variant="outline" asChild>
                <a href="#features">Explore Services</a>
              </Button>
            </div>
            <div className="flex flex-wrap items-center gap-6 pt-2 text-xs font-medium text-slate-500">
              <span className="inline-flex items-center gap-1.5">
                <Lock className="h-4 w-4 text-medical-blue" /> Private User Records
              </span>
              <span className="inline-flex items-center gap-1.5">
                <ShieldCheck className="h-4 w-4 text-medical-cyan" /> Non-Diagnostic Guardrails
              </span>
            </div>
          </div>

          <HeroIllustration />
        </div>
      </section>

      <section id="features" className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div className="mx-auto max-w-2xl text-center">
          <Badge variant="cyan">Comprehensive Modules</Badge>
          <h2 className="mt-3 text-3xl font-bold tracking-tight text-slate-900 sm:text-4xl">
            Intelligent Healthcare Support Tools
          </h2>
          <p className="mt-3 text-slate-600">
            Every module is designed to educate, clarify medical information, and protect patient
            safety.
          </p>
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

      <section id="how-it-works" className="bg-white/80 py-16 border-y border-blue-100">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="mx-auto max-w-2xl text-center">
            <Badge>Simple Workflow</Badge>
            <h2 className="mt-3 text-3xl font-bold tracking-tight text-slate-900">How It Works</h2>
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
          <Badge variant="success">Why Patients & Students Trust It</Badge>
          <h2 className="text-3xl font-bold tracking-tight text-slate-900">
            Clarity Without Guesswork
          </h2>
          <p className="text-slate-600">
            Medical documents can feel overwhelming. AI Medical Assistant breaks down terminology
            transparently while strictly respecting clinical boundaries.
          </p>
          <ul className="space-y-3">
            {benefits.map((b) => (
              <li key={b} className="flex items-start gap-2.5 text-sm text-slate-700">
                <CheckCircle2 className="mt-0.5 h-5 w-5 shrink-0 text-medical-cyan" />
                <span>{b}</span>
              </li>
            ))}
          </ul>
          <Button asChild>
            <Link to="/library">Browse Health Information Library</Link>
          </Button>
        </div>

        <Card id="safety" className="border-blue-200 bg-gradient-to-br from-white to-blue-50/60 p-6">
          <div className="space-y-4">
            <h3 className="text-xl font-bold text-slate-900">Medical Safety & Privacy Commitment</h3>
            <DisclaimerBanner />
            <p className="text-sm leading-relaxed text-slate-600">
              Your uploaded PDFs, images, and chat histories are scoped exclusively to your
              authenticated account, validated server-side, and can be permanently deleted anytime
              from your Personal Health Dashboard.
            </p>
          </div>
        </Card>
      </section>
    </div>
  );
}
