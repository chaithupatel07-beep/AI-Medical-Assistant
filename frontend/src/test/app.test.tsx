import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { describe, expect, it } from "vitest";
import { AiConfigNotice } from "@/components/AiConfigNotice";
import { LanguageSwitcher } from "@/components/LanguageSwitcher";
import { ThemeToggle } from "@/components/ThemeToggle";
import { AuthProvider } from "@/hooks/useAuth";
import { LanguageProvider } from "@/hooks/useLanguage";
import { ThemeProvider } from "@/hooks/useTheme";
import { LandingPage } from "@/pages/LandingPage";
import { LoginPage } from "@/pages/LoginPage";

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

  it("toggles light and dark theme class and shows offline mode info notice", () => {
    document.documentElement.classList.remove("dark");
    renderWithProviders(
      <>
        <ThemeToggle />
        <AiConfigNotice configured={false} mode="built_in_offline" />
      </>
    );
    expect(
      screen.getByText(/Built-in Offline Educational Mode Active/i)
    ).toBeInTheDocument();

    fireEvent.click(screen.getByRole("button", { name: /Switch to dark mode/i }));
    expect(document.documentElement.classList.contains("dark")).toBe(true);
  });
});
