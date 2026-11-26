import { FormEvent, useEffect, useState } from "react";
import { AlertCircle, CheckCircle2, History, Loader2, Stethoscope } from "lucide-react";
import { AiConfigNotice } from "@/components/AiConfigNotice";
import { DisclaimerBanner } from "@/components/DisclaimerBanner";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { api } from "@/services/api";
import type { ActivityItem, SymptomCheckResult } from "@/types/api";
import { formatDateTime } from "@/utils/format";

export function SymptomCheckerPage() {
  const [age, setAge] = useState("28");
  const [gender, setGender] = useState("");
  const [mainSymptom, setMainSymptom] = useState("");
  const [duration, setDuration] = useState("");
  const [severity, setSeverity] = useState<"mild" | "moderate" | "severe">("mild");
  const [additionalSymptoms, setAdditionalSymptoms] = useState("");
  const [relevantContext, setRelevantContext] = useState("");

  const [aiConfigured, setAiConfigured] = useState(true);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<SymptomCheckResult | null>(null);
  const [history, setHistory] = useState<ActivityItem[]>([]);

  const loadHistoryAndHealth = () => {
    Promise.all([api.getSymptomHistory(), api.health()])
      .then(([hist, health]) => {
        setHistory(hist);
        setAiConfigured(health.ai_configured);
      })
      .catch(() => {});
  };

  useEffect(() => {
    loadHistoryAndHealth();
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
        duration: duration.trim(),
        severity,
        additional_symptoms: additionalSymptoms.trim() || undefined,
        relevant_context: relevantContext.trim() || undefined,
      });
      setResult(res);
      loadHistoryAndHealth();
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
          <Stethoscope className="h-6 w-6 text-medical-blue" /> Symptom Information Checker
        </h1>
        <p className="mt-1 text-sm text-slate-600">
          Structured educational guidance to help you understand common possibilities and prepare
          for a medical consultation—never a diagnosis.
        </p>
      </div>

      <AiConfigNotice configured={aiConfigured} />

      <div className="grid gap-6 lg:grid-cols-12">
        <Card className="lg:col-span-5">
          <CardHeader>
            <CardTitle>Symptom Details</CardTitle>
            <CardDescription>Fill in the fields below to generate educational context.</CardDescription>
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
                  <Label htmlFor="sym-age">Age *</Label>
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
                  <Label htmlFor="sym-gender">Gender (optional)</Label>
                  <Input
                    id="sym-gender"
                    placeholder="e.g., Female, Male"
                    value={gender}
                    onChange={(e) => setGender(e.target.value)}
                  />
                </div>
              </div>

              <div className="space-y-1.5">
                <Label htmlFor="sym-main">Main Symptom *</Label>
                <Input
                  id="sym-main"
                  placeholder="e.g., Persistent dry cough, headache"
                  value={mainSymptom}
                  onChange={(e) => setMainSymptom(e.target.value)}
                  required
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div className="space-y-1.5">
                  <Label htmlFor="sym-duration">Duration *</Label>
                  <Input
                    id="sym-duration"
                    placeholder="e.g., 3 days, 2 weeks"
                    value={duration}
                    onChange={(e) => setDuration(e.target.value)}
                    required
                  />
                </div>
                <div className="space-y-1.5">
                  <Label htmlFor="sym-severity">Severity *</Label>
                  <select
                    id="sym-severity"
                    value={severity}
                    onChange={(e) => setSeverity(e.target.value as "mild" | "moderate" | "severe")}
                    className="flex h-10 w-full rounded-lg border border-slate-200 bg-white px-3 text-sm text-slate-900 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-medical-blue"
                  >
                    <option value="mild">Mild</option>
                    <option value="moderate">Moderate</option>
                    <option value="severe">Severe</option>
                  </select>
                </div>
              </div>

              <div className="space-y-1.5">
                <Label htmlFor="sym-add">Additional Symptoms</Label>
                <Textarea
                  id="sym-add"
                  rows={2}
                  placeholder="e.g., Mild fatigue, low-grade fever"
                  value={additionalSymptoms}
                  onChange={(e) => setAdditionalSymptoms(e.target.value)}
                />
              </div>

              <div className="space-y-1.5">
                <Label htmlFor="sym-ctx">Relevant Context (optional)</Label>
                <Textarea
                  id="sym-ctx"
                  rows={2}
                  placeholder="Recent travel, allergies, existing conditions, current medications..."
                  value={relevantContext}
                  onChange={(e) => setRelevantContext(e.target.value)}
                />
              </div>

              <Button type="submit" className="w-full" disabled={loading}>
                {loading ? (
                  <>
                    <Loader2 className="h-4 w-4 animate-spin" /> Analyzing Educational Info...
                  </>
                ) : (
                  "Get Educational Symptom Info"
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
                    <CardTitle>Educational Overview</CardTitle>
                    <Badge>{result.ai_model}</Badge>
                  </div>
                </CardHeader>
                <CardContent className="space-y-5 text-sm text-slate-700">
                  <p className="leading-relaxed">{result.educational_overview}</p>

                  <div>
                    <h3 className="mb-2 font-semibold text-slate-900">
                      Possible Common Explanations (Educational Possibilities — Not a Diagnosis)
                    </h3>
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
                        <CheckCircle2 className="h-4 w-4" /> Recommended Next Steps
                      </h4>
                      <ul className="mt-2 list-disc space-y-1 pl-4">
                        {result.recommended_next_steps.map((step, idx) => (
                          <li key={idx}>{step}</li>
                        ))}
                      </ul>
                    </div>

                    <div className="rounded-xl border border-red-200 bg-red-50/50 p-4">
                      <h4 className="flex items-center gap-1.5 font-semibold text-red-900">
                        <AlertCircle className="h-4 w-4" /> Warning Signs (Seek Urgent Care)
                      </h4>
                      <ul className="mt-2 list-disc space-y-1 pl-4 text-red-900">
                        {result.warning_signs.map((sign, idx) => (
                          <li key={idx}>{sign}</li>
                        ))}
                      </ul>
                    </div>
                  </div>

                  <div className="rounded-xl bg-slate-50 p-4">
                    <h4 className="font-semibold text-slate-900">When to Consult a Doctor</h4>
                    <p className="mt-1">{result.when_to_consult_doctor}</p>
                  </div>

                  {result.questions_for_doctor.length > 0 && (
                    <div>
                      <h4 className="font-semibold text-slate-900">Helpful Questions for Your Doctor</h4>
                      <ul className="mt-1.5 list-disc space-y-1 pl-5">
                        {result.questions_for_doctor.map((q, idx) => (
                          <li key={idx}>{q}</li>
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
                <h2 className="text-lg font-semibold text-slate-900">
                  Structured Educational Symptom Guide
                </h2>
                <p className="text-sm text-slate-500">
                  Submit the form on the left to review non-diagnostic educational possibilities,
                  warning signs, and questions for your clinician.
                </p>
              </div>
            </Card>
          )}

          {history.length > 0 && (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2 text-base">
                  <History className="h-4 w-4 text-medical-blue" /> Recent Symptom Checks
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-2">
                {history.slice(0, 5).map((item) => (
                  <button
                    key={item.id}
                    type="button"
                    onClick={() => loadSavedCheck(item)}
                    className="flex w-full items-center justify-between rounded-xl border border-slate-100 p-3 text-left text-sm hover:bg-slate-50"
                  >
                    <span className="font-medium text-slate-800">{item.description}</span>
                    <span className="text-xs text-slate-500">{formatDateTime(item.created_at)}</span>
                  </button>
                ))}
              </CardContent>
            </Card>
          )}
        </div>
      </div>
    </div>
  );
}
