import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";
import { ProtectedRoute } from "@/components/ProtectedRoute";
import { AuthProvider } from "@/hooks/useAuth";
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

export function App() {
  return (
    <AuthProvider>
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
              <Route path="records" element={<PersonalHealthPage />} />
            </Route>
          </Route>

          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}

export default App;
