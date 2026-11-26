import { useState } from "react";
import { zodResolver } from "@hookform/resolvers/zod";
import { Check, Loader2, UserPlus, X } from "lucide-react";
import { useForm } from "react-hook-form";
import { Link, useNavigate } from "react-router-dom";
import { z } from "zod";
import { DisclaimerBanner } from "@/components/DisclaimerBanner";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { useAuth } from "@/hooks/useAuth";
import { useLanguage } from "@/hooks/useLanguage";
import { evaluatePassword } from "@/utils/validation";

const registerSchema = z
  .object({
    fullName: z.string().trim().min(2, "Full name must be at least 2 characters."),
    email: z.string().trim().email("Please enter a valid email address."),
    password: z
      .string()
      .refine((val) => evaluatePassword(val).valid, {
        message: "Password does not meet complexity requirements.",
      }),
    confirmPassword: z.string(),
  })
  .refine((data) => data.password === data.confirmPassword, {
    path: ["confirmPassword"],
    message: "Passwords do not match.",
  });

type RegisterFormValues = z.infer<typeof registerSchema>;

export function RegisterPage() {
  const { register: registerAccount } = useAuth();
  const { t } = useLanguage();
  const navigate = useNavigate();
  const [serverError, setServerError] = useState<string | null>(null);

  const {
    register,
    watch,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<RegisterFormValues>({
    resolver: zodResolver(registerSchema),
    defaultValues: { fullName: "", email: "", password: "", confirmPassword: "" },
  });

  const passwordVal = watch("password") || "";
  const pwEval = evaluatePassword(passwordVal);

  const onSubmit = async (values: RegisterFormValues) => {
    setServerError(null);
    try {
      await registerAccount(values.fullName.trim(), values.email.trim(), values.password);
      navigate("/dashboard", { replace: true });
    } catch (err) {
      setServerError(err instanceof Error ? err.message : "Registration failed.");
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
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-4" noValidate>
            {serverError && (
              <div className="rounded-lg border border-red-200 bg-red-50 px-3.5 py-2.5 text-sm text-red-700">
                {serverError}
              </div>
            )}

            <div className="space-y-1.5">
              <Label htmlFor="reg-name">{t("auth.fullName")}</Label>
              <Input id="reg-name" {...register("fullName")} />
              {errors.fullName && (
                <p className="text-xs text-red-600">{errors.fullName.message}</p>
              )}
            </div>

            <div className="space-y-1.5">
              <Label htmlFor="reg-email">{t("auth.email")}</Label>
              <Input
                id="reg-email"
                type="email"
                autoComplete="email"
                placeholder="alex@example.com"
                {...register("email")}
              />
              {errors.email && <p className="text-xs text-red-600">{errors.email.message}</p>}
            </div>

            <div className="space-y-1.5">
              <Label htmlFor="reg-password">{t("auth.password")}</Label>
              <Input
                id="reg-password"
                type="password"
                autoComplete="new-password"
                {...register("password")}
              />
              {passwordVal.length > 0 && (
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
              {errors.password && (
                <p className="text-xs text-red-600">{errors.password.message}</p>
              )}
            </div>

            <div className="space-y-1.5">
              <Label htmlFor="reg-confirm">{t("auth.confirmPassword")}</Label>
              <Input
                id="reg-confirm"
                type="password"
                autoComplete="new-password"
                {...register("confirmPassword")}
              />
              {errors.confirmPassword && (
                <p className="text-xs text-red-600">{errors.confirmPassword.message}</p>
              )}
            </div>

            <Button type="submit" className="w-full" disabled={isSubmitting}>
              {isSubmitting ? (
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
