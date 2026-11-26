import { useState } from "react";
import { Menu, X } from "lucide-react";
import { Link, Outlet, useLocation } from "react-router-dom";
import { BrandLogo } from "@/components/BrandLogo";
import { LanguageSwitcher } from "@/components/LanguageSwitcher";
import { ThemeToggle } from "@/components/ThemeToggle";
import { Button } from "@/components/ui/button";
import { useAuth } from "@/hooks/useAuth";
import { useLanguage } from "@/hooks/useLanguage";

export function PublicLayout() {
  const { user } = useAuth();
  const { t } = useLanguage();
  const [mobileOpen, setMobileOpen] = useState(false);
  const location = useLocation();

  const navLinks = [
    { label: t("nav.features"), href: "/#features" },
    { label: t("nav.howItWorks"), href: "/#how-it-works" },
    { label: t("nav.safety"), href: "/#safety" },
    { label: t("nav.library"), href: "/library" },
  ];

  return (
    <div className="flex min-h-screen flex-col">
      <header className="sticky top-0 z-40 border-b border-blue-100/80 bg-white/90 backdrop-blur-md dark:border-slate-800 dark:bg-slate-950/90">
        <div className="mx-auto flex h-16 max-w-7xl items-center justify-between gap-3 px-4 sm:px-6 lg:px-8">
          <BrandLogo />

          <nav className="hidden items-center gap-5 lg:flex">
            {navLinks.map((item) =>
              item.href.startsWith("/#") && location.pathname === "/" ? (
                <a
                  key={item.href}
                  href={item.href.slice(1)}
                  className="text-sm font-medium text-slate-600 transition-colors hover:text-medical-blue dark:text-slate-300 dark:hover:text-cyan-400"
                >
                  {item.label}
                </a>
              ) : (
                <Link
                  key={item.href}
                  to={item.href}
                  className="text-sm font-medium text-slate-600 transition-colors hover:text-medical-blue dark:text-slate-300 dark:hover:text-cyan-400"
                >
                  {item.label}
                </Link>
              )
            )}
          </nav>

          <div className="hidden items-center gap-2.5 md:flex">
            <LanguageSwitcher />
            <ThemeToggle />
            {user ? (
              <Button asChild>
                <Link to="/dashboard">{t("nav.openDashboard")}</Link>
              </Button>
            ) : (
              <>
                <Button variant="ghost" asChild>
                  <Link to="/login">{t("nav.signIn")}</Link>
                </Button>
                <Button asChild>
                  <Link to="/register">{t("nav.getStarted")}</Link>
                </Button>
              </>
            )}
          </div>

          <div className="flex items-center gap-2 md:hidden">
            <LanguageSwitcher />
            <ThemeToggle />
            <button
              type="button"
              className="inline-flex rounded-lg p-2 text-slate-600 hover:bg-slate-100 dark:text-slate-300 dark:hover:bg-slate-800"
              onClick={() => setMobileOpen((prev) => !prev)}
              aria-label="Toggle navigation"
            >
              {mobileOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
            </button>
          </div>
        </div>

        {mobileOpen && (
          <div className="border-t border-slate-100 bg-white px-4 py-4 dark:border-slate-800 dark:bg-slate-900 md:hidden">
            <div className="flex flex-col gap-3">
              {navLinks.map((item) => (
                <Link
                  key={item.href}
                  to={item.href}
                  onClick={() => setMobileOpen(false)}
                  className="rounded-lg px-3 py-2 text-sm font-medium text-slate-700 hover:bg-blue-50"
                >
                  {item.label}
                </Link>
              ))}
              <div className="mt-2 flex gap-2">
                {user ? (
                  <Button asChild className="w-full" onClick={() => setMobileOpen(false)}>
                    <Link to="/dashboard">{t("nav.openDashboard")}</Link>
                  </Button>
                ) : (
                  <>
                    <Button variant="outline" asChild className="flex-1" onClick={() => setMobileOpen(false)}>
                      <Link to="/login">{t("nav.signIn")}</Link>
                    </Button>
                    <Button asChild className="flex-1" onClick={() => setMobileOpen(false)}>
                      <Link to="/register">{t("nav.getStarted")}</Link>
                    </Button>
                  </>
                )}
              </div>
            </div>
          </div>
        )}
      </header>

      <main className="flex-1">
        <Outlet />
      </main>

      <footer className="border-t border-blue-100 bg-white py-10 dark:border-slate-800 dark:bg-slate-950">
        <div className="mx-auto grid max-w-7xl gap-8 px-4 sm:grid-cols-3 sm:px-6 lg:px-8">
          <div className="space-y-3">
            <BrandLogo compact />
            <p className="text-sm text-slate-500 dark:text-slate-400">{t("footer.desc")}</p>
          </div>
          <div>
            <h4 className="text-sm font-semibold text-slate-900 dark:text-slate-100">{t("footer.platform")}</h4>
            <ul className="mt-3 space-y-2 text-sm text-slate-600 dark:text-slate-400">
              <li><Link to="/library" className="hover:text-medical-blue">{t("nav.library")}</Link></li>
              <li><Link to="/register" className="hover:text-medical-blue">{t("footer.createAccount")}</Link></li>
              <li><Link to="/login" className="hover:text-medical-blue">{t("footer.signInPortal")}</Link></li>
            </ul>
          </div>
          <div>
            <h4 className="text-sm font-semibold text-slate-900 dark:text-slate-100">{t("footer.safetyContact")}</h4>
            <ul className="mt-3 space-y-2 text-sm text-slate-600 dark:text-slate-400">
              <li>{t("footer.emergency")}</li>
              <li>{t("footer.support")}</li>
              <li>{t("footer.educationalOnly")}</li>
            </ul>
          </div>
        </div>
        <div className="mx-auto mt-8 max-w-7xl border-t border-slate-100 px-4 pt-6 text-center text-xs text-slate-500 dark:border-slate-800 dark:text-slate-400 sm:px-6 lg:px-8">
          © {new Date().getFullYear()} {t("footer.copyright")}
        </div>
      </footer>
    </div>
  );
}
