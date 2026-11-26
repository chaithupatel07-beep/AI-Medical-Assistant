import { useState } from "react";
import {
  Activity,
  BookOpen,
  FileText,
  FolderHeart,
  Image as ImageIcon,
  LayoutDashboard,
  LogOut,
  Menu,
  MessageSquareHeart,
  Stethoscope,
  X,
} from "lucide-react";
import { NavLink, Outlet, useNavigate } from "react-router-dom";
import { BrandLogo } from "@/components/BrandLogo";
import { Button } from "@/components/ui/button";
import { useAuth } from "@/hooks/useAuth";
import { cn } from "@/utils/cn";

const navItems = [
  { to: "/dashboard", label: "Overview", icon: LayoutDashboard, end: true },
  { to: "/dashboard/chat", label: "AI Medical Chat", icon: MessageSquareHeart },
  { to: "/dashboard/symptoms", label: "Symptom Info", icon: Stethoscope },
  { to: "/dashboard/reports", label: "Report Summarizer", icon: FileText },
  { to: "/dashboard/images", label: "Image Analysis", icon: ImageIcon },
  { to: "/dashboard/library", label: "Health Library", icon: BookOpen },
  { to: "/dashboard/records", label: "Personal Health", icon: FolderHeart },
];

export function DashboardLayout() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [sidebarOpen, setSidebarOpen] = useState(false);

  const handleLogout = async () => {
    await logout();
    navigate("/login");
  };

  const sidebarContent = (
    <div className="flex h-full flex-col justify-between p-4">
      <div className="space-y-6">
        <div className="px-1 pt-1">
          <BrandLogo to="/dashboard" compact />
        </div>

        <nav className="space-y-1">
          {navItems.map((item) => {
            const Icon = item.icon;
            return (
              <NavLink
                key={item.to}
                to={item.to}
                end={item.end}
                onClick={() => setSidebarOpen(false)}
                className={({ isActive }) =>
                  cn(
                    "flex items-center gap-3 rounded-xl px-3.5 py-2.5 text-sm font-medium transition-all",
                    isActive
                      ? "bg-gradient-to-r from-medical-blue to-blue-600 text-white shadow-sm"
                      : "text-slate-600 hover:bg-blue-50 hover:text-medical-blue"
                  )
                }
              >
                <Icon className="h-4 w-4 shrink-0" />
                <span>{item.label}</span>
              </NavLink>
            );
          })}
        </nav>
      </div>

      <div className="space-y-3 border-t border-slate-100 pt-4">
        <div className="rounded-xl bg-blue-50/70 p-3 text-xs text-slate-600">
          <div className="flex items-center gap-1.5 font-semibold text-medical-blue">
            <Activity className="h-3.5 w-3.5" />
            <span>Medical Safety</span>
          </div>
          <p className="mt-1 leading-relaxed">
            Educational support only. For emergencies, call local emergency services immediately.
          </p>
        </div>

        <div className="flex items-center justify-between gap-2 rounded-xl border border-slate-200 bg-white px-3 py-2.5">
          <div className="min-w-0">
            <p className="truncate text-sm font-semibold text-slate-900">{user?.full_name}</p>
            <p className="truncate text-xs text-slate-500">{user?.email}</p>
          </div>
          <Button
            variant="ghost"
            size="icon"
            onClick={handleLogout}
            title="Sign Out"
            aria-label="Sign Out"
          >
            <LogOut className="h-4 w-4 text-slate-600" />
          </Button>
        </div>
      </div>
    </div>
  );

  return (
    <div className="min-h-screen bg-slate-50/70 lg:flex">
      <aside className="hidden w-72 shrink-0 border-r border-blue-100 bg-white lg:block">
        <div className="sticky top-0 h-screen overflow-y-auto">{sidebarContent}</div>
      </aside>

      {sidebarOpen && (
        <div className="fixed inset-0 z-50 flex lg:hidden">
          <div
            className="fixed inset-0 bg-slate-900/40 backdrop-blur-sm"
            onClick={() => setSidebarOpen(false)}
          />
          <aside className="relative z-10 h-full w-72 bg-white shadow-xl">
            <button
              type="button"
              className="absolute right-3 top-3 rounded-lg p-1.5 text-slate-500 hover:bg-slate-100"
              onClick={() => setSidebarOpen(false)}
              aria-label="Close sidebar"
            >
              <X className="h-5 w-5" />
            </button>
            {sidebarContent}
          </aside>
        </div>
      )}

      <div className="flex min-w-0 flex-1 flex-col">
        <header className="sticky top-0 z-30 flex h-16 items-center justify-between border-b border-blue-100 bg-white/90 px-4 backdrop-blur-md lg:hidden">
          <BrandLogo to="/dashboard" compact />
          <button
            type="button"
            className="rounded-lg p-2 text-slate-600 hover:bg-slate-100"
            onClick={() => setSidebarOpen(true)}
            aria-label="Open navigation menu"
          >
            <Menu className="h-5 w-5" />
          </button>
        </header>

        <main className="flex-1 p-4 sm:p-6 lg:p-8">
          <div className="mx-auto max-w-6xl">
            <Outlet />
          </div>
        </main>
      </div>
    </div>
  );
}
