"use client";

import * as React from "react";
import {
  LayoutDashboard,
  CalendarCheck,
  Users,
  Wallet,
  Settings,
  LogOut,
  Bell,
} from "lucide-react";
import { useAuth } from "@/lib/auth-context";
import { useAppStore, type ViewName } from "@/store/app-store";
import { Logo, Wordmark } from "@/components/brand";
import { cn } from "@/lib/utils";
import { toast } from "sonner";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";

const NAV_ITEMS: { view: ViewName; label: string; icon: React.ElementType }[] = [
  { view: "dashboard", label: "Home", icon: LayoutDashboard },
  { view: "attendance", label: "Attend", icon: CalendarCheck },
  { view: "employees", label: "Staff", icon: Users },
  { view: "payroll", label: "Payroll", icon: Wallet },
  { view: "settings", label: "Settings", icon: Settings },
];

export function AppShell({
  children,
  activeView,
}: {
  children: React.ReactNode;
  activeView: ViewName;
}) {
  const { business, user, logout } = useAuth();
  const navigate = useAppStore((s) => s.navigate);
  const [now, setNow] = React.useState<Date | null>(null);

  React.useEffect(() => {
    setNow(new Date());
    const t = setInterval(() => setNow(new Date()), 60000);
    return () => clearInterval(t);
  }, []);

  const handleLogout = async () => {
    await logout();
    toast.success("Signed out");
  };

  const initials = (user?.name || user?.email || "U").slice(0, 2).toUpperCase();

  return (
    <div className="min-h-screen flex flex-col bg-background">
      {/* Header */}
      <header className="sticky top-0 z-30 bg-porcelain/90 backdrop-blur-md border-b border-border/60">
        <div className="max-w-md mx-auto px-4 h-14 flex items-center justify-between">
          <div className="flex items-center gap-2 min-w-0">
            <Logo size={30} />
            <div className="min-w-0">
              <Wordmark className="text-base leading-none" />
              {business && (
                <p className="text-[11px] text-graphite/55 leading-tight truncate max-w-[150px]">
                  {business.name}
                </p>
              )}
            </div>
          </div>
          <div className="flex items-center gap-1">
            <button
              className="size-9 rounded-full flex items-center justify-center text-graphite/60 hover:bg-accent/50 transition-colors"
              aria-label="Notifications"
              onClick={() => toast.info("No new notifications")}
            >
              <Bell className="size-[18px]" />
            </button>
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <button className="rounded-full" aria-label="Account menu">
                  <Avatar className="size-9 border border-border">
                    <AvatarFallback className="bg-jungle-teal text-white text-xs">
                      {initials}
                    </AvatarFallback>
                  </Avatar>
                </button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end" className="w-52">
                <DropdownMenuLabel className="text-xs text-graphite/55">
                  {user?.email}
                </DropdownMenuLabel>
                <DropdownMenuSeparator />
                <DropdownMenuItem onClick={handleLogout} className="text-destructive focus:text-destructive">
                  <LogOut className="size-4 mr-2" /> Sign out
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          </div>
        </div>
      </header>

      {/* Content */}
      <main className="flex-1 max-w-md mx-auto w-full px-4 pb-28 pt-4">
        {now && (
          <p className="text-[11px] text-graphite/60 mb-2 px-1 font-medium">
            {now.toLocaleDateString("en-IN", {
              weekday: "long",
              day: "numeric",
              month: "long",
            })}
          </p>
        )}
        {children}
      </main>

      {/* Bottom nav */}
      <nav className="sticky bottom-0 z-30 bg-porcelain/95 backdrop-blur-md border-t border-border/60 pb-[env(safe-area-inset-bottom)]">
        <div className="max-w-md mx-auto px-2 h-16 flex items-stretch justify-around">
          {NAV_ITEMS.map((item) => {
            const active = activeView === item.view ||
              (item.view === "employees" && activeView === "employee-detail") ||
              (item.view === "payroll" && activeView === "payroll-run");
            const Icon = item.icon;
            return (
              <button
                key={item.view}
                onClick={() => navigate(item.view)}
                className="flex-1 flex flex-col items-center justify-center gap-0.5 relative"
              >
                {active && (
                  <span className="absolute top-0 h-0.5 w-8 rounded-full bg-jungle-teal" />
                )}
                <Icon
                  className={cn(
                    "size-[22px] transition-colors",
                    active ? "text-jungle-teal" : "text-graphite/45"
                  )}
                  strokeWidth={active ? 2.4 : 2}
                />
                <span
                  className={cn(
                    "text-[10px] font-medium transition-colors",
                    active ? "text-jungle-teal" : "text-graphite/45"
                  )}
                >
                  {item.label}
                </span>
              </button>
            );
          })}
        </div>
      </nav>
    </div>
  );
}
