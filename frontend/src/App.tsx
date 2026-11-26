import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";
import { ProtectedRoute } from "@/components/ProtectedRoute";
import { AuthProvider } from "@/hooks/useAuth";
import { LanguageProvider } from "@/hooks/useLanguage";
import { ThemeProvider } from "@/hooks/useTheme";
import { DashboardLayout } from "@/layouts/DashboardLayout";
import { PublicLayout } from "@/layouts/PublicLayout";
import { ChatbotPage } from "@/pages/ChatbotPage";
import { DashboardPage } from "@/pages/DashboardPage";
import { ForgotPasswordPage } from "@/pages/ForgotPasswordPage";
import { HealthLibraryPage } from "@/pages/HealthLibraryPage";
import { LandingPage } from "@/pages/LandingPage";
import { LoginPage } from "@/pages/LoginPage";
import { MedicalImagePage } from "@/pages/MedicalImagePage";
import { PersonalHealthPage } from "@/pages/PersonalHealthPage";
import { RegisterPage } from "@/pages/RegisterPage";
import { ReportSummarizerPage } from "@/pages/ReportSummarizerPage";
import { SymptomCheckerPage } from "@/pages/SymptomCheckerPage";

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
    <QueryClientProvider client={queryClient}>
      <ThemeProvider>
        <AuthProvider>
          <LanguageProvider>
            <BrowserRouter>
              <Routes>
                <Route element={<PublicLayout />}>
                  <Route path="/" element={<LandingPage />} />
                  <Route path="/login" element={<LoginPage />} />
                  <Route path="/register" element={<RegisterPage />} />
                  <Route path="/forgot-password" element={<ForgotPasswordPage />} />
                  <Route path="/library" element={<HealthLibraryPage />} />
                </Route>

                <Route element={<ProtectedRoute />}>
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
            </BrowserRouter>
          </LanguageProvider>
        </AuthProvider>
      </ThemeProvider>
    </QueryClientProvider>
  );
}

export default App;
