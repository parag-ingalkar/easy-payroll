"use client";

import * as React from "react";
import { useAuth } from "@/lib/auth-context";
import { useAppStore } from "@/store/app-store";
import { AppShell } from "@/components/app-shell";
import { Logo } from "@/components/brand";
import { LoginView } from "@/components/views/login-view";
import { RegisterView } from "@/components/views/register-view";
import { OnboardingView } from "@/components/views/onboarding-view";
import { DashboardView } from "@/components/views/dashboard-view";
import { AttendanceView } from "@/components/views/attendance-view";
import { EmployeesView } from "@/components/views/employees-view";
import { EmployeeDetailView } from "@/components/views/employee-detail-view";
import { PayrollView } from "@/components/views/payroll-view";
import { PayrollRunView } from "@/components/views/payroll-run-view";
import { SettingsView } from "@/components/views/settings-view";

function SplashScreen() {
  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-background gap-4">
      <div className="pp-animate-in">
        <Logo size={64} />
      </div>
      <div className="flex gap-1.5">
        <span className="size-2 rounded-full bg-jungle-teal pp-pulse-dot" style={{ animationDelay: "0ms" }} />
        <span className="size-2 rounded-full bg-jungle-teal pp-pulse-dot" style={{ animationDelay: "160ms" }} />
        <span className="size-2 rounded-full bg-jungle-teal pp-pulse-dot" style={{ animationDelay: "320ms" }} />
      </div>
    </div>
  );
}

export default function Home() {
  const { user, business, loading } = useAuth();
  const view = useAppStore((s) => s.view);
  const params = useAppStore((s) => s.params);

  if (loading) return <SplashScreen />;

  // Not authenticated
  if (!user) {
    if (view === "register") return <RegisterView />;
    return <LoginView />;
  }

  // Owner authenticated but no business yet → onboarding
  if (!business) {
    return <OnboardingView />;
  }

  // Authenticated with business → app shell
  let content: React.ReactNode;
  switch (view) {
    case "attendance":
      content = <AttendanceView />;
      break;
    case "employees":
      content = <EmployeesView />;
      break;
    case "employee-detail":
      content = <EmployeeDetailView employeeId={params.id} />;
      break;
    case "payroll":
      content = <PayrollView />;
      break;
    case "payroll-run":
      content = <PayrollRunView runId={params.id} />;
      break;
    case "settings":
      content = <SettingsView />;
      break;
    case "dashboard":
    default:
      content = <DashboardView />;
      break;
  }

  return <AppShell activeView={view}>{content}</AppShell>;
}
