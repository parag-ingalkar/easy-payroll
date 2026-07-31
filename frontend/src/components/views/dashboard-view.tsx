"use client";

import * as React from "react";
import { useQuery } from "@tanstack/react-query";
import {
  BarChart,
  Bar,
  XAxis,
  ResponsiveContainer,
  Tooltip,
} from "recharts";
import {
  Wallet,
  AlertCircle,
  ArrowRight,
  CheckCircle2,
  UserPlus,
  BarChart3,
} from "lucide-react";
import { apiFetch } from "@/lib/api";
import { useAppStore } from "@/store/app-store";
import { useAuth } from "@/lib/auth-context";
import { formatCurrency } from "@/lib/format";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { cn } from "@/lib/utils";
import type { DashboardShape } from "@/lib/types";

type TrendDay = DashboardShape["trend"][number];
type PayrollMonth = DashboardShape["payrollHistory"][number];

export function DashboardView() {
  const navigate = useAppStore((s) => s.navigate);
  const { business } = useAuth();

  const { data, isLoading } = useQuery({
    queryKey: ["dashboard", business?.id],
    queryFn: () =>
      apiFetch<DashboardShape>(`/api/business/${business!.id}/dashboard`),
    enabled: !!business?.id,
  });

  if (isLoading || !data) {
    return <DashboardSkeleton />;
  }

  const payrollNotRun = data.payroll.status === "not_run";
  const hasEmployees = data.activeEmployees > 0;

  return (
    <div className="space-y-5 pp-animate-in">
      {/* Greeting */}
      <div>
        <h1 className="text-2xl font-bold text-graphite">{data.business.name}</h1>
        <p className="text-sm text-graphite/55">
          {data.monthName} {data.year} overview
        </p>
      </div>

      {/* Payroll status — the one primary metric on this surface */}
      <Card className="bg-jungle-teal text-white border-0 p-5 shadow-md shadow-jungle-teal/20">
        <div className="flex items-center justify-between mb-1.5">
          <span className="text-[11px] font-medium text-white/75 tracking-wide">
            {data.monthName} payroll
          </span>
          {payrollNotRun ? (
            <span className="text-[10px] px-2 py-0.5 rounded-full bg-white/20 font-medium">Not run</span>
          ) : (
            <span className="text-[10px] px-2 py-0.5 rounded-full bg-white/20 font-medium capitalize">
              {data.payroll.status}
            </span>
          )}
        </div>
        <p className="text-[2rem] font-bold tracking-tight leading-none">
          {formatCurrency(data.payroll.totalPayable)}
        </p>
        <p className="text-[13px] text-white/80 mt-2">
          {payrollNotRun
            ? hasEmployees
              ? `Projected ~${formatCurrency(data.projectedMonthlyCost)} from base rates`
              : "Add employees to get started"
            : `${data.payroll.paidCount} of ${data.payroll.totalCount} employees paid`}
        </p>
        <div className="flex items-center justify-between mt-4 gap-3">
          <Button
            onClick={() => navigate("payroll")}
            variant="secondary"
            className="bg-white/15 hover:bg-white/25 text-white border-0 h-9"
          >
            {payrollNotRun ? "Run payroll" : "View payroll"}
            <ArrowRight className="size-4" />
          </Button>
          {data.ytdPaid > 0 && (
            <div className="text-right">
              <p className="text-[10px] text-white/65">YTD paid</p>
              <p className="text-sm font-semibold tabular-nums">{formatCurrency(data.ytdPaid)}</p>
            </div>
          )}
        </div>
      </Card>

      {/* Today — team status */}
      {hasEmployees && (
        <Card className="bg-porcelain shadow-sm p-4">
          <div className="flex items-center justify-between mb-3">
            <h2 className="text-[13px] font-semibold text-graphite">Today</h2>
            <button
              onClick={() => navigate("attendance")}
              className="text-[11px] font-medium text-jungle-teal hover:underline"
            >
              {data.pendingAttendance > 0 ? `${data.pendingAttendance} pending` : "View attendance"}
            </button>
          </div>
          <div className="flex items-end gap-4">
            <div>
              <p className="text-2xl font-bold text-graphite leading-none tabular-nums">
                {data.presentToday}
                <span className="text-base font-medium text-graphite/45">/{data.activeEmployees}</span>
              </p>
              <p className="text-[11px] text-graphite/55 mt-1">present</p>
            </div>
            <div className="h-8 w-px bg-border/60" />
            <div className="flex flex-col gap-1">
              <div className="flex items-center gap-1.5">
                <span className="size-1.5 rounded-full bg-amber-500" />
                <span className="text-xs text-graphite/70">{data.halfToday} half day</span>
              </div>
              <div className="flex items-center gap-1.5">
                <span className="size-1.5 rounded-full bg-sky-500" />
                <span className="text-xs text-graphite/70">{data.onLeaveToday} on leave</span>
              </div>
            </div>
            <div className="ml-auto text-right">
              <p className="text-xs text-graphite/55">Active staff</p>
              <p className="text-lg font-semibold text-graphite tabular-nums">{data.activeEmployees}</p>
            </div>
          </div>
        </Card>
      )}

      {/* This month — finances */}
      {hasEmployees && (data.monthlyAdditions > 0 || data.monthlyDeductions > 0) && (
        <Card className="bg-porcelain shadow-sm p-4">
          <h2 className="text-[13px] font-semibold text-graphite mb-3">{data.monthName} finances</h2>
          <div className="grid grid-cols-2 gap-4">
            <button onClick={() => navigate("employees")} className="text-left group">
              <p className="text-[11px] text-graphite/55">Additions</p>
              <p className="text-base font-semibold text-emerald-700 tabular-nums">
                {formatCurrency(data.monthlyAdditions)}
              </p>
            </button>
            <button onClick={() => navigate("employees")} className="text-left group">
              <p className="text-[11px] text-graphite/55">Deductions</p>
              <p className="text-base font-semibold text-rose-700 tabular-nums">
                {formatCurrency(data.monthlyDeductions)}
              </p>
            </button>
          </div>
        </Card>
      )}

      {/* Attendance trend (7 days) */}
      {hasEmployees && data.trend.length > 0 && (
        <Card className="bg-porcelain shadow-sm p-4">
          <div className="flex items-center justify-between mb-3">
            <div className="flex items-center gap-2">
              <div className="size-7 rounded-lg bg-accent flex items-center justify-center">
                <BarChart3 className="size-4 text-jungle-teal" />
              </div>
              <h2 className="text-sm font-semibold text-graphite">Attendance trend</h2>
            </div>
            <span className="text-[10px] text-graphite/60">Last 7 days</span>
          </div>
          <TrendChart data={data.trend} />
          <div className="flex items-center justify-center gap-4 mt-2 text-[10px]">
            <LegendDot color="bg-emerald-500" label="Present" />
            <LegendDot color="bg-amber-500" label="Half" />
            <LegendDot color="bg-sky-500" label="Leave" />
            <LegendDot color="bg-rose-300" label="Absent" />
          </div>
        </Card>
      )}

      {/* Payroll history (6 months) */}
      {data.payrollHistory.some((m) => m.total > 0) && (
        <Card className="bg-porcelain shadow-sm p-4">
          <div className="flex items-center justify-between mb-3">
            <div className="flex items-center gap-2">
              <div className="size-7 rounded-lg bg-accent flex items-center justify-center">
                <Wallet className="size-4 text-jungle-teal" />
              </div>
              <h2 className="text-sm font-semibold text-graphite">Payroll history</h2>
            </div>
            <span className="text-[10px] text-graphite/60">Last 6 months</span>
          </div>
          <PayrollHistoryChart data={data.payrollHistory} />
        </Card>
      )}

      {/* Quick actions */}
      {(() => {
        const hasPending = data.pendingAttendance > 0;
        const hasPayrollTodo = payrollNotRun && hasEmployees;
        const noEmployees = data.activeEmployees === 0;
        const anyAction = hasPending || hasPayrollTodo || noEmployees;
        return (
          <div className="space-y-3">
            <h2 className="text-sm font-semibold text-graphite/70 uppercase tracking-wide px-1">
              Quick actions
            </h2>
            {hasPending && (
              <ActionRow
                icon={AlertCircle}
                tint="bg-amber-100 text-amber-700"
                title={`${data.pendingAttendance} employees need attendance`}
                desc="Mark today's attendance to keep records accurate."
                actionLabel="Mark now"
                onAction={() => navigate("attendance")}
              />
            )}
            {hasPayrollTodo && (
              <ActionRow
                icon={Wallet}
                tint="bg-jungle-teal/15 text-jungle-teal"
                title="Run this month's payroll"
                desc="Calculate salaries, OT, additions & deductions."
                actionLabel="Run"
                onAction={() => navigate("payroll")}
              />
            )}
            {noEmployees && (
              <ActionRow
                icon={UserPlus}
                tint="bg-sky-100 text-sky-700"
                title="Add your first employee"
                desc="Add staff to start tracking attendance and payroll."
                actionLabel="Add"
                onAction={() => navigate("employees")}
              />
            )}
            {!anyAction && (
              <Card className="p-5 bg-porcelain shadow-sm">
                <div className="flex items-center gap-3">
                  <div className="size-10 rounded-xl bg-emerald-100 flex items-center justify-center shrink-0">
                    <CheckCircle2 className="size-5 text-emerald-600" />
                  </div>
                  <div>
                    <p className="text-sm font-medium text-graphite">You&apos;re all caught up!</p>
                    <p className="text-xs text-graphite/55">
                      Attendance marked &amp; payroll ready. Great work managing your team.
                    </p>
                  </div>
                </div>
              </Card>
            )}
          </div>
        );
      })()}
    </div>
  );
}

function TrendChart({ data }: { data: TrendDay[] }) {
  return (
    <div className="h-32 -ml-2">
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={data} barCategoryGap="22%" margin={{ top: 4, right: 4, bottom: 0, left: 0 }}>
          <XAxis
            dataKey="day"
            tick={{ fontSize: 10, fill: "var(--muted-foreground)" }}
            axisLine={false}
            tickLine={false}
          />
          <Tooltip
            cursor={{ fill: "var(--accent)", fillOpacity: 0.4 }}
            content={<TrendTooltip />}
          />
          <Bar dataKey="present" stackId="a" fill="#10b981" radius={[0, 0, 0, 0]} maxBarSize={26} />
          <Bar dataKey="half" stackId="a" fill="#f59e0b" maxBarSize={26} />
          <Bar dataKey="leave" stackId="a" fill="#0ea5e9" maxBarSize={26} />
          <Bar dataKey="absent" stackId="a" fill="#fda4af" radius={[4, 4, 0, 0]} maxBarSize={26} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}

function TrendTooltip({ active, payload }: any) {
  if (!active || !payload?.length) return null;
  const d = payload[0].payload as TrendDay;
  return (
    <div className="bg-porcelain border border-border/60 rounded-lg shadow-md p-2 text-xs">
      <p className="font-semibold text-graphite mb-1">{d.day} · {d.date}</p>
      <div className="space-y-0.5">
        <p className="text-emerald-700">Present: {d.present}</p>
        <p className="text-amber-700">Half: {d.half}</p>
        <p className="text-sky-700">Leave: {d.leave}</p>
        <p className="text-rose-500">Absent: {d.absent}</p>
      </div>
    </div>
  );
}

function PayrollHistoryChart({ data }: { data: PayrollMonth[]; }) {
  const maxVal = Math.max(...data.map((d) => d.total), 1);
  return (
    <div className="space-y-2.5">
      {data.map((m) => {
        const heightPct = maxVal > 0 ? (m.total / maxVal) * 100 : 0;
        const paidPct = m.total > 0 ? (m.paid / m.total) * 100 : 0;
        return (
          <div key={m.label + m.month} className="flex items-center gap-3">
            <span className="text-[11px] font-medium text-graphite/55 w-7 text-right">{m.label}</span>
            <div className="flex-1 h-7 bg-muted rounded-lg overflow-hidden relative">
              <div
                className="h-full bg-jungle-teal/20 rounded-lg transition-all duration-500"
                style={{ width: `${heightPct}%` }}
              />
              <div
                className="absolute top-0 left-0 h-full bg-jungle-teal rounded-lg transition-all duration-700"
                style={{ width: `${(heightPct * paidPct) / 100}%` }}
              />
              <span className="absolute right-2 top-1/2 -translate-y-1/2 text-[10px] font-semibold text-graphite">
                {m.total > 0 ? formatCurrency(m.total).replace("₹", "") : "—"}
              </span>
            </div>
          </div>
        );
      })}
      <div className="flex items-center justify-center gap-4 pt-1 text-[10px]">
        <LegendDot color="bg-jungle-teal" label="Paid" />
        <LegendDot color="bg-jungle-teal/20" label="Total payable" />
      </div>
    </div>
  );
}

function LegendDot({ color, label }: { color: string; label: string }) {
  return (
    <span className="flex items-center gap-1 text-graphite/55">
      <span className={cn("size-2 rounded-full", color)} />
      {label}
    </span>
  );
}

function ActionRow({
  icon: Icon,
  tint,
  title,
  desc,
  actionLabel,
  onAction,
}: {
  icon: React.ElementType;
  tint: string;
  title: string;
  desc: string;
  actionLabel: string;
  onAction: () => void;
}) {
  return (
    <Card className="p-4 bg-porcelain shadow-sm hover:shadow-md transition-shadow">
      <div className="flex items-center gap-3">
        <div className={`size-10 rounded-xl flex items-center justify-center shrink-0 ${tint}`}>
          <Icon className="size-5" />
        </div>
        <div className="flex-1 min-w-0">
          <p className="text-sm font-medium text-graphite">{title}</p>
          <p className="text-xs text-graphite/55">{desc}</p>
        </div>
        <Button size="sm" className="bg-jungle-teal hover:bg-jungle-teal/90 text-white" onClick={onAction}>
          {actionLabel}
        </Button>
      </div>
    </Card>
  );
}

function DashboardSkeleton() {
  return (
    <div className="space-y-5">
      <div className="space-y-2">
        <div className="h-7 w-48 bg-graphite/10 rounded-lg shimmer" />
        <div className="h-4 w-32 bg-graphite/10 rounded-lg shimmer" />
      </div>
      <div className="h-36 bg-graphite/10 rounded-2xl shimmer" />
      <div className="h-20 bg-graphite/10 rounded-2xl shimmer" />
      <div className="h-40 bg-graphite/10 rounded-2xl shimmer" />
    </div>
  );
}
