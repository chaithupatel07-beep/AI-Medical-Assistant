import { FormEvent, useEffect, useState } from "react";
import { AlertCircle, CheckCircle2, Download, History, Languages, Loader2, Stethoscope, Trash2 } from "lucide-react";
import { DisclaimerBanner } from "@/components/DisclaimerBanner";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { useLanguage } from "@/hooks/useLanguage";
import { api } from "@/services/api";
import type { ActivityItem, SymptomCheckResult } from "@/types/api";
import { formatDateTime } from "@/utils/format";

export function SymptomCheckerPage() {
  const { language, t } = useLanguage();
  const [age, setAge] = useState("28");
  const [gender, setGender] = useState("");
  const [mainSymptom, setMainSymptom] = useState("");
  const [duration, setDuration] = useState("");
  const [severity, setSeverity] = useState<"mild" | "moderate" | "severe">("mild");
  const [severityScore, setSeverityScore] = useState<number>(3);
  const [symptomOnset, setSymptomOnset] = useState("");
  const [frequency, setFrequency] = useState("");
  const [aggravatingFactors, setAggravatingFactors] = useState("");
  const [relievingFactors, setRelievingFactors] = useState("");
  const [showBilingualQuestions, setShowBilingualQuestions] = useState(false);
  const [additionalSymptoms, setAdditionalSymptoms] = useState("");
  const [relevantContext, setRelevantContext] = useState("");

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<SymptomCheckResult | null>(null);
  const [history, setHistory] = useState<ActivityItem[]>([]);

  const loadHistory = () => {
    api
      .getSymptomHistory()
      .then((hist) => {
        setHistory(hist);
      })
      .catch(() => { });
  };

  useEffect(() => {
    loadHistory();
  }, []);

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setError(null);
    const parsedAge = Number(age);
    if (!Number.isInteger(parsedAge) || parsedAge < 0 || parsedAge > 120) {
      setError("Please enter a valid age between 0 and 120.");
      return;
    }
    if (mainSymptom.trim().length < 2) {
      setError("Please describe the main symptom.");
      return;
    }
    if (!duration.trim()) {
      setError("Please specify how long symptoms have lasted.");
      return;
    }

    setLoading(true);
    try {
      const res = await api.checkSymptoms({
        age: parsedAge,
        gender: gender.trim() || undefined,
        main_symptom: mainSymptom.trim(),
        symptom_onset: symptomOnset.trim() || undefined,
        duration: duration.trim(),
        frequency: frequency.trim() || undefined,
        severity,
        severity_score: severityScore,
        aggravating_factors: aggravatingFactors.trim() || undefined,
        relieving_factors: relievingFactors.trim() || undefined,
        additional_symptoms: additionalSymptoms.trim() || undefined,
        relevant_context: relevantContext.trim() || undefined,
        language,
      });
      setResult(res);
      loadHistory();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to analyze symptom information.");
    } finally {
      setLoading(false);
    }
  };

  const loadSavedCheck = (item: ActivityItem) => {
    if (!item.metadata_json) return;
    try {
      const parsed = JSON.parse(item.metadata_json);
      if (parsed?.response) {
        setResult({
          activity_id: item.id,
          ai_model: parsed.ai_model || "saved",
          ...parsed.response,
        });
      }
    } catch {
      // ignore malformed metadata
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="flex items-center gap-2.5 text-2xl font-bold text-slate-900">
          <Stethoscope className="h-6 w-6 text-medical-blue" /> {t("sym.title")}
        </h1>
        <p className="mt-1 text-sm text-slate-600">{t("sym.sub")}</p>
      </div>

      <div className="grid gap-6 lg:grid-cols-12">
        <Card className="lg:col-span-5">
          <CardHeader>
            <CardTitle>{t("sym.details")}</CardTitle>
            <CardDescription>{t("sym.detailsSub")}</CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-4">
              {error && (
                <div className="rounded-lg border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-700">
                  {error}
                </div>
              )}

              <div className="grid grid-cols-2 gap-3">
                <div className="space-y-1.5">
                  <Label htmlFor="sym-age">{t("sym.age")}</Label>
                  <Input
                    id="sym-age"
                    type="number"
                    min={0}
                    max={120}
                    value={age}
                    onChange={(e) => setAge(e.target.value)}
                    required
                  />
                </div>
                <div className="space-y-1.5">
                  <Label htmlFor="sym-gender">{t("sym.gender")}</Label>
                  <Input
                    id="sym-gender"
                    value={gender}
                    onChange={(e) => setGender(e.target.value)}
                  />
                </div>
              </div>

              <div className="space-y-1.5">
                <Label htmlFor="sym-main">{t("sym.main")}</Label>
                <Input
                  id="sym-main"
                  value={mainSymptom}
                  onChange={(e) => setMainSymptom(e.target.value)}
                  required
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div className="space-y-1.5">
                  <Label htmlFor="sym-duration">{t("sym.duration")}</Label>
                  <Input
                    id="sym-duration"
                    value={duration}
                    onChange={(e) => setDuration(e.target.value)}
                    required
                  />
                </div>
                <div className="space-y-1.5">
                  <Label htmlFor="sym-severity">{t("sym.severity")}</Label>
                  <select
                    id="sym-severity"
                    value={severity}
                    onChange={(e) => {
                      const val = e.target.value as "mild" | "moderate" | "severe";
                      setSeverity(val);
                      setSeverityScore(val === "mild" ? 3 : val === "moderate" ? 6 : 9);
                    }}
                    className="flex h-10 w-full rounded-lg border border-slate-200 bg-white px-3 text-sm text-slate-900 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-medical-blue dark:border-slate-700 dark:bg-slate-900 dark:text-slate-100"
                  >
                    <option value="mild">{t("sym.mild")}</option>
                    <option value="moderate">{t("sym.moderate")}</option>
                    <option value="severe">{t("sym.severe")}</option>
                  </select>
                </div>
              </div>

              <div className="space-y-1.5">
                <div className="flex items-center justify-between text-xs">
                  <Label htmlFor="sym-score">{t("sym.severityScale")}</Label>
                  <span className="font-semibold text-medical-blue">{severityScore} / 10</span>
                </div>
                <input
                  id="sym-score"
                  type="range"
                  min={1}
                  max={10}
                  value={severityScore}
                  onChange={(e) => {
                    const next = Number(e.target.value);
                    setSeverityScore(next);
                    setSeverity(next <= 3 ? "mild" : next <= 7 ? "moderate" : "severe");
                  }}
                  className="h-2 w-full cursor-pointer accent-medical-blue"
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div className="space-y-1.5">
                  <Label htmlFor="sym-onset">{t("sym.onset")}</Label>
                  <Input
                    id="sym-onset"
                    value={symptomOnset}
                    onChange={(e) => setSymptomOnset(e.target.value)}
                  />
                </div>
                <div className="space-y-1.5">
                  <Label htmlFor="sym-freq">{t("sym.frequency")}</Label>
                  <Input
                    id="sym-freq"
                    value={frequency}
                    onChange={(e) => setFrequency(e.target.value)}
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div className="space-y-1.5">
                  <Label htmlFor="sym-agg">{t("sym.aggravating")}</Label>
                  <Input
                    id="sym-agg"
                    value={aggravatingFactors}
                    onChange={(e) => setAggravatingFactors(e.target.value)}
                  />
                </div>
                <div className="space-y-1.5">
                  <Label htmlFor="sym-rel">{t("sym.relieving")}</Label>
                  <Input
                    id="sym-rel"
                    value={relievingFactors}
                    onChange={(e) => setRelievingFactors(e.target.value)}
                  />
                </div>
              </div>

              <div className="space-y-1.5">
                <Label htmlFor="sym-add">{t("sym.additional")}</Label>
                <Textarea
                  id="sym-add"
                  rows={2}
                  value={additionalSymptoms}
                  onChange={(e) => setAdditionalSymptoms(e.target.value)}
                />
              </div>

              <div className="space-y-1.5">
                <Label htmlFor="sym-ctx">{t("sym.context")}</Label>
                <Textarea
                  id="sym-ctx"
                  rows={2}
                  value={relevantContext}
                  onChange={(e) => setRelevantContext(e.target.value)}
                />
              </div>

              <Button type="submit" className="w-full" disabled={loading}>
                {loading ? (
                  <>
                    <Loader2 className="h-4 w-4 animate-spin" /> {t("sym.analyzing")}
                  </>
                ) : (
                  t("sym.submit")
                )}
              </Button>
            </form>
          </CardContent>
        </Card>

        <div className="space-y-4 lg:col-span-7">
          {result ? (
            <div className="space-y-4">
              {result.emergency_detected && result.emergency_banner && (
                <DisclaimerBanner
                  variant="emergency"
                  message={result.emergency_banner}
                  reasons={result.emergency_reasons}
                />
              )}

              <Card>
                <CardHeader>
                  <div className="flex items-center justify-between gap-2">
                    <CardTitle>{t("sym.overview")}</CardTitle>
                    <Badge>{result.ai_model}</Badge>
                  </div>
                </CardHeader>
                <CardContent className="space-y-5 text-sm text-slate-700">
                  <p className="leading-relaxed">{result.educational_overview}</p>

                  <div>
                    <h3 className="mb-2 font-semibold text-slate-900">{t("sym.possibilities")}</h3>
                    <div className="space-y-2.5">
                      {result.possible_explanations.map((item, idx) => (
                        <div key={idx} className="rounded-xl border border-blue-100 bg-blue-50/40 p-3.5">
                          <p className="font-semibold text-slate-900">{item.title}</p>
                          <p className="mt-1 text-slate-600">{item.description}</p>
                        </div>
                      ))}
                    </div>
                  </div>

                  <div className="grid gap-4 sm:grid-cols-2">
                    <div className="rounded-xl border border-emerald-100 bg-emerald-50/40 p-4">
                      <h4 className="flex items-center gap-1.5 font-semibold text-emerald-900">
                        <CheckCircle2 className="h-4 w-4" /> {t("sym.nextSteps")}
                      </h4>
                      <ul className="mt-2 list-disc space-y-1 pl-4">
                        {result.recommended_next_steps.map((step, idx) => (
                          <li key={idx}>{step}</li>
                        ))}
                      </ul>
                    </div>

                    <div className="rounded-xl border border-red-200 bg-red-50/50 p-4">
                      <h4 className="flex items-center gap-1.5 font-semibold text-red-900">
                        <AlertCircle className="h-4 w-4" /> {t("sym.warnings")}
                      </h4>
                      <ul className="mt-2 list-disc space-y-1 pl-4 text-red-900">
                        {result.warning_signs.map((sign, idx) => (
                          <li key={idx}>{sign}</li>
                        ))}
                      </ul>
                    </div>
                  </div>

                  <div className="rounded-xl bg-slate-50 p-4">
                    <h4 className="font-semibold text-slate-900">{t("sym.whenDoctor")}</h4>
                    <p className="mt-1">{result.when_to_consult_doctor}</p>
                  </div>

                  {result.questions_for_doctor.length > 0 && (
                    <div className="space-y-2">
                      <div className="flex flex-wrap items-center justify-between gap-2">
                        <h4 className="font-semibold text-slate-900 dark:text-slate-100">{t("sym.questions")}</h4>
                        <div className="flex flex-wrap items-center gap-2">
                          {language !== "en" && (result.questions_for_doctor_en?.length ?? 0) > 0 && (
                            <Button
                              type="button"
                              size="sm"
                              variant="outline"
                              onClick={() => setShowBilingualQuestions((prev) => !prev)}
                            >
                              <Languages className="h-3.5 w-3.5" /> {t("sym.bilingualBtn")}
                            </Button>
                          )}
                          <Button
                            type="button"
                            size="sm"
                            variant="outline"
                            onClick={() => {
                              const lines = [
                                "AI Medical Assistant — Questions to Ask Your Doctor",
                                "--------------------------------------------------",
                                ...result.questions_for_doctor.map((q, idx) => `${idx + 1}. ${q}`),
                                ...(showBilingualQuestions && result.questions_for_doctor_en?.length
                                  ? [
                                    "",
                                    "English Reference:",
                                    ...result.questions_for_doctor_en.map((q, idx) => `${idx + 1}. ${q}`),
                                  ]
                                  : []),
                                "",
                                result.disclaimer,
                              ];
                              const blob = new Blob([lines.join("\n")], { type: "text/plain;charset=utf-8" });
                              const url = URL.createObjectURL(blob);
                              const a = document.createElement("a");
                              a.href = url;
                              a.download = "questions-for-doctor.txt";
                              a.click();
                              URL.revokeObjectURL(url);
                            }}
                          >
                            <Download className="h-3.5 w-3.5" /> {t("sym.exportQuestions")}
                          </Button>
                        </div>
                      </div>
                      <ul className="list-disc space-y-1.5 pl-5">
                        {result.questions_for_doctor.map((q, idx) => (
                          <li key={idx}>
                            <span>{q}</span>
                            {showBilingualQuestions && result.questions_for_doctor_en?.[idx] && (
                              <span className="block text-xs text-slate-500">
                                ({result.questions_for_doctor_en[idx]})
                              </span>
                            )}
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}

                  <DisclaimerBanner message={result.disclaimer} />
                </CardContent>
              </Card>
            </div>
          ) : (
            <Card className="flex min-h-[260px] items-center justify-center p-8 text-center">
              <div className="max-w-md space-y-2">
                <Stethoscope className="mx-auto h-10 w-10 text-medical-cyan" />
                <h2 className="text-lg font-semibold text-slate-900">{t("sym.emptyTitle")}</h2>
                <p className="text-sm text-slate-500">{t("sym.emptySub")}</p>
              </div>
            </Card>
          )}

          {history.length > 0 && (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2 text-base">
                  <History className="h-4 w-4 text-medical-blue" /> {t("sym.recent")}
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-2">
                {history.slice(0, 5).map((item) => (
                  <div
                    key={item.id}
                    className="flex items-center justify-between gap-2 rounded-xl border border-slate-100 p-3 text-sm hover:bg-slate-50 dark:border-slate-800 dark:hover:bg-slate-800/60"
                  >
                    <button
                      type="button"
                      onClick={() => loadSavedCheck(item)}
                      className="min-w-0 flex-1 text-left"
                    >
                      <span className="block truncate font-medium text-slate-800 dark:text-slate-200">{item.description}</span>
                      <span className="text-xs text-slate-500">{formatDateTime(item.created_at)}</span>
                    </button>
                    <button
                      type="button"
                      aria-label="Delete symptom record"
                      onClick={() => {
                        void api.deleteSymptomEntry(item.id).then(() => {
                          setHistory((prev) => prev.filter((x) => x.id !== item.id));
                        });
                      }}
                      className="rounded-lg p-1.5 text-slate-400 hover:bg-red-50 hover:text-red-600"
                    >
                      <Trash2 className="h-4 w-4" />
                    </button>
                  </div>
                ))}
              </CardContent>
            </Card>
          )}
        </div>
      </div>
    </div>
  );
}
