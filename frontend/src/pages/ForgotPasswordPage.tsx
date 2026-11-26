import { FormEvent, useState } from "react";
import { KeyRound, Loader2 } from "lucide-react";
import { Link } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { useLanguage } from "@/hooks/useLanguage";
import { api } from "@/services/api";
import { evaluatePassword, isValidEmail } from "@/utils/validation";

export function ForgotPasswordPage() {
  const { t } = useLanguage();
  const [email, setEmail] = useState("");
  const [token, setToken] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [step, setStep] = useState<"request" | "reset" | "done">("request");
  const [infoMessage, setInfoMessage] = useState<string | null>(null);
  const [devToken, setDevToken] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const handleRequestToken = async (e: FormEvent) => {
    e.preventDefault();
    setError(null);
    if (!isValidEmail(email)) {
      setError("Please enter a valid email address.");
      return;
    }

    setLoading(true);
    try {
      const res = await api.forgotPassword(email.trim());
      setInfoMessage(res.message);
      if (res.reset_token) {
        setDevToken(res.reset_token);
        setToken(res.reset_token);
      }
      setStep("reset");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not initiate password reset.");
    } finally {
      setLoading(false);
    }
  };

  const handleResetPassword = async (e: FormEvent) => {
    e.preventDefault();
    setError(null);
    const pwCheck = evaluatePassword(newPassword);
    if (!pwCheck.valid) {
      setError(pwCheck.message);
      return;
    }

    setLoading(true);
    try {
      const res = await api.resetPassword({ token: token.trim(), new_password: newPassword });
      setInfoMessage(res.message);
      setStep("done");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to reset password.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="mx-auto max-w-md px-4 py-12">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-2xl">
            <KeyRound className="h-5 w-5 text-medical-blue" /> {t("auth.recoveryTitle")}
          </CardTitle>
          <CardDescription>{t("auth.recoverySub")}</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {error && (
            <div className="rounded-lg border border-red-200 bg-red-50 px-3.5 py-2.5 text-sm text-red-700">
              {error}
            </div>
          )}
          {infoMessage && (
            <div className="rounded-lg border border-blue-200 bg-blue-50 px-3.5 py-2.5 text-sm text-slate-800">
              {infoMessage}
            </div>
          )}

          {step === "request" && (
            <form onSubmit={handleRequestToken} className="space-y-4">
              <div className="space-y-1.5">
                <Label htmlFor="fp-email">{t("auth.accountEmail")}</Label>
                <Input
                  id="fp-email"
                  type="email"
                  placeholder="you@example.com"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  required
                />
              </div>
              <Button type="submit" className="w-full" disabled={loading}>
                {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : t("auth.genToken")}
              </Button>
            </form>
          )}

          {step === "reset" && (
            <form onSubmit={handleResetPassword} className="space-y-4">
              {devToken && (
                <div className="rounded-lg border border-cyan-200 bg-cyan-50 p-3 text-xs text-cyan-900">
                  <p className="font-semibold">Development Mode Preview Token</p>
                  <p className="mt-1 break-all font-mono">{devToken}</p>
                </div>
              )}

              <div className="space-y-1.5">
                <Label htmlFor="fp-token">{t("auth.resetToken")}</Label>
                <Input
                  id="fp-token"
                  value={token}
                  onChange={(e) => setToken(e.target.value)}
                  required
                />
              </div>

              <div className="space-y-1.5">
                <Label htmlFor="fp-new-pw">{t("auth.newPassword")}</Label>
                <Input
                  id="fp-new-pw"
                  type="password"
                  value={newPassword}
                  onChange={(e) => setNewPassword(e.target.value)}
                  required
                />
              </div>

              <Button type="submit" className="w-full" disabled={loading}>
                {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : t("auth.resetBtn")}
              </Button>
            </form>
          )}

          {step === "done" && (
            <Button asChild className="w-full">
              <Link to="/login">{t("auth.proceedSignIn")}</Link>
            </Button>
          )}

          <p className="text-center text-sm text-slate-600">
            <Link to="/login" className="text-medical-blue hover:underline">
              {t("auth.backSignIn")}
            </Link>
          </p>
        </CardContent>
      </Card>
    </div>
  );
}
