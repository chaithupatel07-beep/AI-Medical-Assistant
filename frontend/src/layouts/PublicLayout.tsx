import { useState } from "react";
import { Menu, X } from "lucide-react";
import { Link, Outlet, useLocation } from "react-router-dom";
import { BrandLogo } from "@/components/BrandLogo";
import { Button } from "@/components/ui/button";
import { useAuth } from "@/hooks/useAuth";

export function PublicLayout() {
  const { user } = useAuth();
  const [mobileOpen, setMobileOpen] = useState(false);
  const location = useLocation();

  const navLinks = [
    { label: "Features", href: "/#features" },
    { label: "How It Works", href: "/#how-it-works" },
    { label: "Safety", href: "/#safety" },
    { label: "Health Library", href: "/library" },
  ];

  return (
    <div className="flex min-h-screen flex-col">
      <header className="sticky top-0 z-40 border-b border-blue-100/80 bg-white/90 backdrop-blur-md">
        <div className="mx-auto flex h-16 max-w-7xl items-center justify-between px-4 sm:px-6 lg:px-8">
          <BrandLogo />

          <nav className="hidden items-center gap-6 md:flex">
            {navLinks.map((item) =>
              item.href.startsWith("/#") && location.pathname === "/" ? (
                <a
                  key={item.label}
                  href={item.href.slice(1)}
                  className="text-sm font-medium text-slate-600 transition-colors hover:text-medical-blue"
                >
                  {item.label}
                </a>
              ) : (
                <Link
                  key={item.label}
                  to={item.href}
                  className="text-sm font-medium text-slate-600 transition-colors hover:text-medical-blue"
                >
                  {item.label}
                </Link>
              )
            )}
          </nav>

          <div className="hidden items-center gap-3 md:flex">
            {user ? (
              <Button asChild>
                <Link to="/dashboard">Open Dashboard</Link>
              </Button>
            ) : (
              <>
                <Button variant="ghost" asChild>
                  <Link to="/login">Sign In</Link>
                </Button>
                <Button asChild>
                  <Link to="/register">Get Started</Link>
                </Button>
              </>
            )}
          </div>

          <button
            type="button"
            className="inline-flex rounded-lg p-2 text-slate-600 hover:bg-slate-100 md:hidden"
            onClick={() => setMobileOpen((prev) => !prev)}
            aria-label="Toggle navigation"
          >
            {mobileOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
          </button>
        </div>

        {mobileOpen && (
          <div className="border-t border-slate-100 bg-white px-4 py-4 md:hidden">
            <div className="flex flex-col gap-3">
              {navLinks.map((item) => (
                <Link
                  key={item.label}
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
                    <Link to="/dashboard">Open Dashboard</Link>
                  </Button>
                ) : (
                  <>
                    <Button variant="outline" asChild className="flex-1" onClick={() => setMobileOpen(false)}>
                      <Link to="/login">Sign In</Link>
                    </Button>
                    <Button asChild className="flex-1" onClick={() => setMobileOpen(false)}>
                      <Link to="/register">Get Started</Link>
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

      <footer className="border-t border-blue-100 bg-white py-10">
        <div className="mx-auto grid max-w-7xl gap-8 px-4 sm:grid-cols-3 sm:px-6 lg:px-8">
          <div className="space-y-3">
            <BrandLogo compact />
            <p className="text-sm text-slate-500">
              Educational healthcare assistance designed to help you understand lab reports,
              symptoms, and trusted health resources.
            </p>
          </div>
          <div>
            <h4 className="text-sm font-semibold text-slate-900">Platform</h4>
            <ul className="mt-3 space-y-2 text-sm text-slate-600">
              <li><Link to="/library" className="hover:text-medical-blue">Health Information Library</Link></li>
              <li><Link to="/register" className="hover:text-medical-blue">Create Free Account</Link></li>
              <li><Link to="/login" className="hover:text-medical-blue">Patient Portal Sign In</Link></li>
            </ul>
          </div>
          <div>
            <h4 className="text-sm font-semibold text-slate-900">Safety & Contact</h4>
            <ul className="mt-3 space-y-2 text-sm text-slate-600">
              <li>Emergency: Call 911 / 112 / local emergency care</li>
              <li>Support: support@aimedicalassistant.edu</li>
              <li>Educational platform — not a substitute for clinical care</li>
            </ul>
          </div>
        </div>
        <div className="mx-auto mt-8 max-w-7xl border-t border-slate-100 px-4 pt-6 text-center text-xs text-slate-500 sm:px-6 lg:px-8">
          © {new Date().getFullYear()} AI Medical Assistant. For educational health support only.
        </div>
      </footer>
    </div>
  );
}
