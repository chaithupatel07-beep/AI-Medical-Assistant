import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { describe, expect, it, vi } from "vitest";
import { LanguageSwitcher } from "@/components/LanguageSwitcher";
import { ProtectedRoute } from "@/components/ProtectedRoute";
import { ThemeToggle } from "@/components/ThemeToggle";
import { AuthProvider, useAuth } from "@/hooks/useAuth";
import { LanguageProvider } from "@/hooks/useLanguage";
import { ThemeProvider } from "@/hooks/useTheme";
import { LandingPage } from "@/pages/LandingPage";
import { LoginPage } from "@/pages/LoginPage";
import { ApiError, setAuthToken, setCachedUser } from "@/services/api";

function renderWithProviders(ui: React.ReactElement) {
  return render(
    <ThemeProvider>
      <AuthProvider>
        <LanguageProvider>
          <MemoryRouter>{ui}</MemoryRouter>
        </LanguageProvider>
      </AuthProvider>
    </ThemeProvider>
  );
}

describe("AI Medical Assistant Frontend", () => {
  it("renders landing page hero, services, privacy handling card, safety disclaimer, and FAQ", () => {
    renderWithProviders(<LandingPage />);
    expect(screen.getByText(/Smarter with AI/i)).toBeInTheDocument();
    expect(screen.getByText(/AI Medical Chatbot/i)).toBeInTheDocument();
    expect(screen.getByText(/How Your Data Is Handled/i)).toBeInTheDocument();
    expect(screen.getByText(/Common Questions About AI Medical Assistant/i)).toBeInTheDocument();
    expect(screen.getByText(/Educational Healthcare Information Only/i)).toBeInTheDocument();
  });

  it("switches UI text between English, Telugu, and Hindi", async () => {
    renderWithProviders(
      <>
        <LanguageSwitcher />
        <LandingPage />
      </>
    );

    fireEvent.click(screen.getByRole("button", { name: "తెలుగు" }));
    await waitFor(() => {
      expect(screen.getByText(/AI తో మరింత స్మార్ట్‌గా/)).toBeInTheDocument();
    });

    fireEvent.click(screen.getByRole("button", { name: "हिन्दी" }));
    await waitFor(() => {
      expect(screen.getByText(/AI के साथ अधिक स्मार्ट/)).toBeInTheDocument();
    });

    fireEvent.click(screen.getByRole("button", { name: "English" }));
    await waitFor(() => {
      expect(screen.getByText(/Smarter with AI/i)).toBeInTheDocument();
    });
  });

  it("validates login form inputs with Zod + React Hook Form", async () => {
    renderWithProviders(<LoginPage />);
    fireEvent.click(screen.getByRole("button", { name: /Sign In/i }));
    await waitFor(() => {
      expect(screen.getByText(/Please enter a valid email address/i)).toBeInTheDocument();
    });
  });

  it("toggles light and dark theme class cleanly", () => {
    document.documentElement.classList.remove("dark");
    renderWithProviders(<ThemeToggle />);

    fireEvent.click(screen.getByRole("button", { name: /Switch to dark mode/i }));
    expect(document.documentElement.classList.contains("dark")).toBe(true);
  });

  it("keeps user logged in across transient server errors and only logs out on explicit sign-out", async () => {
    setAuthToken("valid.jwt.token");
    setCachedUser({
      id: "u-1",
      email: "patient@example.com",
      full_name: "Patient One",
      created_at: new Date().toISOString(),
      profile: null,
    });

    const fetchSpy = vi
      .spyOn(globalThis, "fetch")
      .mockResolvedValue(new Response(JSON.stringify({ detail: "Temporary 502" }), { status: 502, headers: { "content-type": "application/json" } }));

    function ProtectedView() {
      const { user, logout } = useAuth();
      return (
        <div>
          <span>Signed in as {user?.email}</span>
          <button type="button" onClick={() => void logout()}>
            Sign Out Test
          </button>
        </div>
      );
    }

    render(
      <ThemeProvider>
        <AuthProvider>
          <LanguageProvider>
            <MemoryRouter initialEntries={["/dashboard"]}>
              <Routes>
                <Route element={<ProtectedRoute />}>
                  <Route path="/dashboard" element={<ProtectedView />} />
                </Route>
                <Route path="/login" element={<div>Login Redirect</div>} />
              </Routes>
            </MemoryRouter>
          </LanguageProvider>
        </AuthProvider>
      </ThemeProvider>
    );

    await waitFor(() => {
      expect(screen.getByText(/Signed in as patient@example\.com/i)).toBeInTheDocument();
    });
    expect(screen.queryByText(/Login Redirect/i)).not.toBeInTheDocument();

    fireEvent.click(screen.getByRole("button", { name: /Sign Out Test/i }));
    await waitFor(() => {
      expect(screen.getByText(/Login Redirect/i)).toBeInTheDocument();
    });

    fetchSpy.mockRestore();
    void ApiError;
  });
});
