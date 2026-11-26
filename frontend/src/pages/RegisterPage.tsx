import { FormEvent, useState } from "react";
import { Check, Loader2, UserPlus, X } from "lucide-react";
import { Link, useNavigate } from "react-router-dom";
import { DisclaimerBanner } from "@/components/DisclaimerBanner";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { useAuth } from "@/hooks/useAuth";
import { useLanguage } from "@/hooks/useLanguage";
import { evaluatePassword, isValidEmail } from "@/utils/validation";

export function RegisterPage() {
  const { register } = useAuth();
  const { t } = useLanguage();
  const navigate = useNavigate();

  const [fullName, setFullName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  const pwEval = evaluatePassword(password);

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setError(null);

    if (fullName.trim().length < 2) {
      setError("Full name must be at least 2 characters.");
      return;
    }
    if (!isValidEmail(email)) {
      setError("Please enter a valid email address.");
      return;
    }
    if (!pwEval.valid) {
      setError(pwEval.message);
      return;
    }
    if (password !== confirmPassword) {
      setError("Passwords do not match.");
      return;
    }

    setSubmitting(true);
    try {
      await register(fullName.trim(), email.trim(), password);
      navigate("/dashboard", { replace: true });
    } catch (err) {
      setError(err instanceof Error ? err.message : "Registration failed.");
    } finally {
      setSubmitting(false);
    }
  };

  const ruleItems = [
    { label: t("auth.pwLen"), ok: pwEval.checks.length },
    { label: t("auth.pwUpper"), ok: pwEval.checks.upper },
    { label: t("auth.pwLower"), ok: pwEval.checks.lower },
    { label: t("auth.pwDigit"), ok: pwEval.checks.digit },
    { label: t("auth.pwSpecial"), ok: pwEval.checks.special },
  ];

  return (
    <div className="mx-auto flex max-w-md flex-col gap-6 px-4 py-12">
      <Card>
        <CardHeader>
          <CardTitle className="text-2xl">{t("auth.createTitle")}</CardTitle>
          <CardDescription>{t("auth.createSub")}</CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            {error && (
              <div className="rounded-lg border border-red-200 bg-red-50 px-3.5 py-2.5 text-sm text-red-700">
                {error}
              </div>
            )}

            <div className="space-y-1.5">
              <Label htmlFor="reg-name">{t("auth.fullName")}</Label>
              <Input
                id="reg-name"
                value={fullName}
                onChange={(e) => setFullName(e.target.value)}
                required
              />
            </div>

            <div className="space-y-1.5">
              <Label htmlFor="reg-email">{t("auth.email")}</Label>
              <Input
                id="reg-email"
                type="email"
                autoComplete="email"
                placeholder="alex@example.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
              />
            </div>

            <div className="space-y-1.5">
              <Label htmlFor="reg-password">{t("auth.password")}</Label>
              <Input
                id="reg-password"
                type="password"
                autoComplete="new-password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
              />
              {password.length > 0 && (
                <div className="mt-2 grid grid-cols-2 gap-1.5 rounded-lg bg-slate-50 p-2.5 text-xs">
                  {ruleItems.map((item) => (
                    <div
                      key={item.label}
                      className={`flex items-center gap-1.5 ${
                        item.ok ? "text-emerald-700" : "text-slate-500"
                      }`}
                    >
                      {item.ok ? <Check className="h-3.5 w-3.5" /> : <X className="h-3.5 w-3.5" />}
                      <span>{item.label}</span>
                    </div>
                  ))}
                </div>
              )}
            </div>

            <div className="space-y-1.5">
              <Label htmlFor="reg-confirm">{t("auth.confirmPassword")}</Label>
              <Input
                id="reg-confirm"
                type="password"
                autoComplete="new-password"
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                required
              />
            </div>

            <Button type="submit" className="w-full" disabled={submitting}>
              {submitting ? (
                <>
                  <Loader2 className="h-4 w-4 animate-spin" /> {t("auth.creating")}
                </>
              ) : (
                <>
                  <UserPlus className="h-4 w-4" /> {t("auth.createBtn")}
                </>
              )}
            </Button>
          </form>

          <p className="mt-5 text-center text-sm text-slate-600">
            {t("auth.alreadyAccount")}{" "}
            <Link to="/login" className="font-semibold text-medical-blue hover:underline">
              {t("nav.signIn")}
            </Link>
          </p>
        </CardContent>
      </Card>

      <DisclaimerBanner />
    </div>
  );
}
