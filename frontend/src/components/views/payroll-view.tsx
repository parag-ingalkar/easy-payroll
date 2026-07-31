"use client";

import * as React from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";
import {
  ChevronLeft,
  ChevronRight,
  Play,
  Wallet,
  CheckCircle2,
  Clock,
  RefreshCw,
  ChevronRight as ChevR,
  CalendarDays,
} from "lucide-react";
import { apiFetch } from "@/lib/api";
import { useAuth } from "@/lib/auth-context";
import { useAppStore } from "@/store/app-store";
import { formatCurrency, formatCurrencyCompact, MONTH_NAMES, MONTH_SHORT } from "@/lib/format";
import type { PayrollRunShape } from "@/lib/types";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";

type RunSummary = PayrollRunShape;

export function PayrollView() {
  const navigate = useAppStore((s) => s.navigate);
  const { business } = useAuth();
  const queryClient = useQueryClient();

  const now = new Date();
  const [selYear, setSelYear] = React.useState(now.getFullYear());
  const [selMonth, setSelMonth] = React.useState(now.getMonth() + 1);

  const { data: runs, isLoading } = useQuery({
    queryKey: ["payroll-runs", business?.id],
    queryFn: () =>
      apiFetch<RunSummary[]>(`/api/business/${business!.id}/payroll`),
    enabled: !!business?.id,
  });

  const runMutation = useMutation({
    mutationFn: () =>
      apiFetch<RunSummary>(`/api/business/${business!.id}/payroll`, {
        method: "POST",
        body: JSON.stringify({ year: selYear, month: selMonth }),
      }),
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ["payroll-runs", business?.id] });
      queryClient.invalidateQueries({ queryKey: ["dashboard"] });
      toast.success("Payroll calculated!");
      navigate("payroll-run", { id: data.id });
    },
    onError: (err) => toast.error(err instanceof Error ? err.message : "Failed to run payroll"),
  });

  const goPrevMonth = () => {
    if (selMonth === 1) { setSelMonth(12); setSelYear((y) => y - 1); }
    else setSelMonth((m) => m - 1);
  };
  const goNextMonth = () => {
    if (selMonth === 12) { setSelMonth(1); setSelYear((y) => y + 1); }
    else setSelMonth((m) => m + 1);
  };

  const selectedRun = runs?.find((r) => r.year === selYear && r.month === selMonth);
  const otherRuns = (runs ?? [])
    .filter((r) => !(r.year === selYear && r.month === selMonth))
    .sort((a, b) => b.year - a.year || b.month - a.month);

  // Year-to-date summary stats
  const thisYearRuns = (runs ?? []).filter((r) => r.year === now.getFullYear());
  const ytdTotal = thisYearRuns.reduce((s, r) => s + r.totalAmountDue, 0);
  const ytdPaid = thisYearRuns.reduce((s, r) => {
    const itemCount = r.lineItems?.length ?? 0;
    const paidCount = r.lineItems?.filter((l) => l.status === "paid").length ?? 0;
    if (r.isPaid || paidCount === itemCount) return s + r.totalAmountDue;
    if (itemCount > 0) return s + r.totalAmountDue * (paidCount / itemCount);
    return s;
  }, 0);
  const avgMonthly = thisYearRuns.length > 0 ? ytdTotal / thisYearRuns.length : 0;
  const runsCount = thisYearRuns.length;

  return (
    <div className="space-y-4 pp-animate-in">
      <div>
        <h1 className="text-xl font-bold text-graphite">Payroll</h1>
      </div>

      {/* Year-to-date summary */}
      {runsCount > 0 && (
        <Card className="bg-porcelain shadow-sm p-4">
          <div className="flex items-center justify-between mb-3">
            <h2 className="text-xs font-semibold text-graphite/70 uppercase tracking-wide">
              {now.getFullYear()} summary
            </h2>
            <Badge variant="secondary" className="text-[10px] h-5">{runsCount} run{runsCount !== 1 ? "s" : ""}</Badge>
          </div>
          <div className="grid grid-cols-3 gap-2">
            <SummaryStat label="Total payable" value={formatCurrencyCompact(ytdTotal)} icon={Wallet} tint="text-jungle-teal" />
            <SummaryStat label="Paid out" value={formatCurrencyCompact(ytdPaid)} icon={CheckCircle2} tint="text-emerald-600" />
            <SummaryStat label="Avg / month" value={formatCurrencyCompact(avgMonthly)} icon={CalendarDays} tint="text-violet-600" />
          </div>
        </Card>
      )}

      {/* Month selector */}
      <Card className="bg-porcelain shadow-sm p-4">
        <div className="flex items-center justify-between mb-3">
          <button onClick={goPrevMonth} className="size-9 rounded-lg flex items-center justify-center hover:bg-accent/50 text-graphite/70">
            <ChevronLeft className="size-5" />
          </button>
          <div className="text-center">
            <p className="text-sm font-semibold text-graphite">{MONTH_NAMES[selMonth - 1]}</p>
            <p className="text-[11px] text-graphite/50">{selYear}</p>
          </div>
          <button
            onClick={goNextMonth}
            disabled={selYear === now.getFullYear() && selMonth === now.getMonth() + 1}
            className="size-9 rounded-lg flex items-center justify-center hover:bg-accent/50 text-graphite/70 disabled:opacity-30"
          >
            <ChevronRight className="size-5" />
          </button>
        </div>

        {selectedRun ? (
          <div className="bg-accent/40 rounded-xl p-3.5">
            <div className="flex items-center justify-between mb-2">
              <div className="flex items-center gap-2">
                <StatusBadge status={selectedRun.status} />
                <span className="text-xs text-graphite/55">
                  {selectedRun.lineItems?.length ?? 0} employees
                </span>
              </div>
              <span className="text-lg font-bold text-graphite">
                {formatCurrency(selectedRun.totalAmountDue)}
              </span>
            </div>
            <div className="flex gap-2 mt-3">
              <Button
                size="sm"
                className="flex-1 bg-jungle-teal hover:bg-jungle-teal/90 text-white h-9"
                onClick={() => navigate("payroll-run", { id: selectedRun.id })}
              >
                View details <ChevR className="size-4" />
              </Button>
              <Button
                size="sm"
                variant="outline"
                className="h-9 px-3"
                onClick={() => runMutation.mutate()}
                disabled={runMutation.isPending}
                title="Recalculate"
              >
                <RefreshCw className={cn("size-4", runMutation.isPending && "animate-spin")} />
                <span className="text-xs">Recalc</span>
              </Button>
            </div>
          </div>
        ) : (
          <div className="bg-muted rounded-xl p-4 text-center">
            <Wallet className="size-7 text-graphite/30 mx-auto" />
            <p className="text-sm font-medium text-graphite/70 mt-2">
              Payroll not run for {MONTH_NAMES[selMonth - 1]} {selYear}
            </p>
            <p className="text-xs text-graphite/50 mt-0.5">
              Run payroll to calculate salaries, OT, additions &amp; deductions.
            </p>
            <Button
              className="mt-3 bg-jungle-teal hover:bg-jungle-teal/90 text-white h-10"
              onClick={() => runMutation.mutate()}
              disabled={runMutation.isPending}
            >
              {runMutation.isPending ? (
                <><RefreshCw className="size-4 animate-spin" /> Calculating…</>
              ) : (
                <><Play className="size-4" /> Run payroll</>
              )}
            </Button>
          </div>
        )}
      </Card>

      {/* Previous runs */}
      {otherRuns.length > 0 && (
        <div className="space-y-2">
          <h2 className="text-sm font-semibold text-graphite/70 uppercase tracking-wide px-1">
            Previous runs
          </h2>
          <div className="space-y-2">
            {otherRuns.map((r) => {
              const empCount = r.lineItems?.length ?? 0;
              const paidCount = r.lineItems?.filter((l) => l.status === "paid").length ?? 0;
              return (
                <button
                  key={r.id}
                  onClick={() => navigate("payroll-run", { id: r.id })}
                  className="w-full text-left bg-porcelain rounded-2xl border border-border/60 p-3.5 shadow-sm hover:shadow-md transition-all active:scale-[0.99]"
                >
                  <div className="flex items-center gap-3">
                    <div className="size-11 rounded-xl bg-accent flex flex-col items-center justify-center shrink-0">
                      <span className="text-[9px] font-medium text-graphite/50 uppercase">
                        {MONTH_SHORT[r.month - 1]}
                      </span>
                      <span className="text-sm font-bold text-jungle-teal leading-none">{r.year}</span>
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium text-graphite">
                        {MONTH_NAMES[r.month - 1]} {r.year}
                      </p>
                      <p className="text-[11px] text-graphite/55">
                        {empCount} employees · {paidCount}/{empCount} paid
                      </p>
                    </div>
                    <div className="text-right shrink-0">
                      <p className="text-sm font-semibold text-graphite">
                        {formatCurrency(r.totalAmountDue)}
                      </p>
                      <StatusBadge status={r.status} />
                    </div>
                    <ChevR className="size-4 text-graphite/30 shrink-0" />
                  </div>
                </button>
              );
            })}
          </div>
        </div>
      )}

      {!isLoading && (runs ?? []).length === 0 && (
        <Card className="p-8 text-center bg-porcelain">
          <CalendarDays className="size-10 text-graphite/30 mx-auto" />
          <p className="text-sm text-graphite/55 mt-2">
            No payroll runs yet. Select a month above and run payroll to get started.
          </p>
        </Card>
      )}
    </div>
  );
}

function SummaryStat({
  label,
  value,
  icon: Icon,
  tint,
}: {
  label: string;
  value: string;
  icon: React.ElementType;
  tint: string;
}) {
  return (
    <div className="bg-muted rounded-xl p-2.5 text-center">
      <Icon className={cn("size-4 mx-auto mb-1", tint)} />
      <p className="text-sm font-bold text-graphite leading-tight tabular-nums">{value}</p>
      <p className="text-[9px] text-graphite/50 mt-0.5">{label}</p>
    </div>
  );
}

function StatusBadge({ status }: { status: string }) {
  const map: Record<string, { label: string; cls: string }> = {
    draft: { label: "Draft", cls: "bg-amber-100 text-amber-700" },
    finalized: { label: "Finalized", cls: "bg-sky-100 text-sky-700" },
    paid: { label: "Paid", cls: "bg-emerald-100 text-emerald-700" },
    not_run: { label: "Not run", cls: "bg-graphite/10 text-graphite/50" },
  };
  const m = map[status] ?? map.draft;
  return (
    <span className={cn("inline-flex items-center gap-1 text-[10px] px-2 py-0.5 rounded-full font-medium", m.cls)}>
      {status === "paid" && <CheckCircle2 className="size-3" />}
      {status === "draft" && <Clock className="size-3" />}
      {m.label}
    </span>
  );
}
