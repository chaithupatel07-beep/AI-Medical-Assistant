import { lazy, Suspense } from "react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";
import { ErrorBoundary } from "@/components/ErrorBoundary";
import { ProtectedRoute } from "@/components/ProtectedRoute";
import { AuthProvider } from "@/hooks/useAuth";
import { LanguageProvider } from "@/hooks/useLanguage";
import { ThemeProvider } from "@/hooks/useTheme";
import { DashboardLayout } from "@/layouts/DashboardLayout";
import { PublicLayout } from "@/layouts/PublicLayout";
import { ForgotPasswordPage } from "@/pages/ForgotPasswordPage";
import { HealthLibraryPage } from "@/pages/HealthLibraryPage";
import { LandingPage } from "@/pages/LandingPage";
import { LoginPage } from "@/pages/LoginPage";
import { RegisterPage } from "@/pages/RegisterPage";

const DashboardPage = lazy(() =>
  import("@/pages/DashboardPage").then((m) => ({ default: m.DashboardPage }))
);
const ChatbotPage = lazy(() =>
  import("@/pages/ChatbotPage").then((m) => ({ default: m.ChatbotPage }))
);
const SymptomCheckerPage = lazy(() =>
  import("@/pages/SymptomCheckerPage").then((m) => ({ default: m.SymptomCheckerPage }))
);
const ReportSummarizerPage = lazy(() =>
  import("@/pages/ReportSummarizerPage").then((m) => ({ default: m.ReportSummarizerPage }))
);
const MedicalImagePage = lazy(() =>
  import("@/pages/MedicalImagePage").then((m) => ({ default: m.MedicalImagePage }))
);
const PersonalHealthPage = lazy(() =>
  import("@/pages/PersonalHealthPage").then((m) => ({ default: m.PersonalHealthPage }))
);

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      refetchOnWindowFocus: false,
    },
  },
});

export function App() {
  return (
    <ErrorBoundary>
      <QueryClientProvider client={queryClient}>
        <ThemeProvider>
          <AuthProvider>
            <LanguageProvider>
              <BrowserRouter>
                <Suspense
                  fallback={
                    <div className="flex min-h-screen items-center justify-center bg-slate-50 text-sm text-slate-600 dark:bg-slate-950 dark:text-slate-300">
                      Loading...
                    </div>
                  }
                >
                  <Routes>
                    <Route element={<PublicLayout />}>
                      <Route path="/" element={<LandingPage />} />
                      <Route path="/login" element={<LoginPage />} />
                      <Route path="/register" element={<RegisterPage />} />
                      <Route path="/forgot-password" element={<ForgotPasswordPage />} />
                      <Route path="/library" element={<HealthLibraryPage />} />
                    </Route>

                    <Route element={<ProtectedRoute />}>
                      <Route element={<DashboardLayout />}>
                        <Route path="/chat" element={<ChatbotPage />} />
                        <Route path="/symptoms" element={<SymptomCheckerPage />} />
                        <Route path="/reports" element={<ReportSummarizerPage />} />
                        <Route path="/image-analysis" element={<MedicalImagePage />} />
                      </Route>
                      <Route path="/dashboard" element={<DashboardLayout />}>
                        <Route index element={<DashboardPage />} />
                        <Route path="chat" element={<ChatbotPage />} />
                        <Route path="symptoms" element={<SymptomCheckerPage />} />
                        <Route path="reports" element={<ReportSummarizerPage />} />
                        <Route path="images" element={<MedicalImagePage />} />
                        <Route path="library" element={<HealthLibraryPage />} />
                        <Route path="records" element={<PersonalHealthPage initialTab="reports" />} />
                        <Route path="history" element={<PersonalHealthPage initialTab="activity" />} />
                        <Route path="profile" element={<PersonalHealthPage initialTab="profile" />} />
                        <Route path="settings" element={<PersonalHealthPage initialTab="profile" />} />
                      </Route>
                    </Route>

                    <Route path="*" element={<Navigate to="/" replace />} />
                  </Routes>
                </Suspense>
              </BrowserRouter>
            </LanguageProvider>
          </AuthProvider>
        </ThemeProvider>
      </QueryClientProvider>
    </ErrorBoundary>
  );
}

export default App;
