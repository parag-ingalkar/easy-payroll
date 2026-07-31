"use client";

import * as React from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";
import {
  ArrowLeft,
  ChevronDown,
  CheckCircle2,
  Banknote,
  Smartphone,
  Building2,
  CheckCheck,
  Stamp,
  TrendingUp,
  Clock,
  FileText,
  Download,
  FileSpreadsheet,
} from "lucide-react";
import { openSalarySlipPrint } from "@/lib/slip-print";
import { exportPayrollCSV } from "@/lib/csv-export";
import { apiFetch } from "@/lib/api";
import { useAuth } from "@/lib/auth-context";
import { useAppStore } from "@/store/app-store";
import { formatCurrency, MONTH_NAMES, formatDate } from "@/lib/format";
import type { PayrollRunShape, PayrollLineItemShape } from "@/lib/types";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import {
  Collapsible,
  CollapsibleContent,
  CollapsibleTrigger,
} from "@/components/ui/collapsible";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
  DialogClose,
  DialogTrigger,
} from "@/components/ui/dialog";
import { cn } from "@/lib/utils";

export function PayrollRunView({ runId }: { runId: string }) {
  const navigate = useAppStore((s) => s.navigate);
  const { business } = useAuth();
  const queryClient = useQueryClient();

  const { data: run, isLoading } = useQuery({
    queryKey: ["payroll-run", business?.id, runId],
    queryFn: () =>
      apiFetch<PayrollRunShape>(`/api/business/${business!.id}/payroll/${runId}`),
    enabled: !!business?.id && !!runId,
  });

  const finalizeMutation = useMutation({
    mutationFn: () =>
      apiFetch<PayrollRunShape>(
        `/api/business/${business!.id}/payroll/${runId}/finalize`,
        { method: "PATCH" },
      ),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["payroll-run", business?.id, runId] });
      queryClient.invalidateQueries({ queryKey: ["payroll-runs", business?.id] });
      queryClient.invalidateQueries({ queryKey: ["dashboard"] });
      toast.success("Payroll finalized");
    },
    onError: (err) => toast.error(err instanceof Error ? err.message : "Failed"),
  });

  const markPaidMutation = useMutation({
    mutationFn: ({ lineItemId, paidVia }: { lineItemId: string; paidVia: string }) =>
      apiFetch<PayrollRunShape>(
        `/api/business/${business!.id}/payroll/${runId}/line-items/${lineItemId}/pay`,
        {
          method: "PATCH",
          body: JSON.stringify({ paidVia }),
        },
      ),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["payroll-run", business?.id, runId] });
      queryClient.invalidateQueries({ queryKey: ["payroll-runs", business?.id] });
      queryClient.invalidateQueries({ queryKey: ["dashboard"] });
      toast.success("Marked as paid");
    },
    onError: (err) => toast.error(err instanceof Error ? err.message : "Failed"),
  });

  const markAllPaidMutation = useMutation({
    mutationFn: (paidVia: string) =>
      apiFetch<PayrollRunShape>(
        `/api/business/${business!.id}/payroll/${runId}/pay-all`,
        {
          method: "PATCH",
          body: JSON.stringify({ paidVia }),
        },
      ),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["payroll-run", business?.id, runId] });
      queryClient.invalidateQueries({ queryKey: ["payroll-runs", business?.id] });
      queryClient.invalidateQueries({ queryKey: ["dashboard"] });
      toast.success("All salaries marked as paid!");
    },
    onError: (err) => toast.error(err instanceof Error ? err.message : "Failed"),
  });

  if (isLoading || !run) {
    return (
      <div className="space-y-4">
        <button onClick={() => navigate("payroll")} className="flex items-center gap-1 text-sm text-graphite/60">
          <ArrowLeft className="size-4" /> Payroll
        </button>
        <div className="h-40 bg-graphite/10 rounded-2xl animate-pulse" />
      </div>
    );
  }

  const lineItems = run.lineItems ?? [];
  const totalPayable = lineItems.reduce((s, l) => s + l.netPayable, 0);
  const totalOt = lineItems.reduce((s, l) => s + l.overtimePay, 0);
  const totalAdditions = lineItems.reduce((s, l) => s + l.totalAdditions, 0);
  const totalDeductions = lineItems.reduce((s, l) => s + l.totalDeductions, 0);
  const paidCount = lineItems.filter((l) => l.status === "paid").length;
  const allPaid = paidCount === lineItems.length && lineItems.length > 0;

  return (
    <div className="space-y-4 pp-animate-in">
      <button
        onClick={() => navigate("payroll")}
        className="flex items-center gap-1 text-sm text-graphite/60 hover:text-graphite"
      >
        <ArrowLeft className="size-4" /> Payroll
      </button>

      {/* Summary hero */}
      <Card className="bg-jungle-teal text-white border-0 shadow-md overflow-hidden relative">
        <div className="absolute -right-8 -top-8 size-32 rounded-full bg-white/10" />
        <div className="relative p-5">
          <div className="flex items-center justify-between mb-1">
            <span className="text-xs font-medium text-white/70 uppercase tracking-wide">
              {MONTH_NAMES[run.month - 1]} {run.year}
            </span>
            <StatusPill status={run.status} />
          </div>
          <p className="text-3xl font-bold">{formatCurrency(totalPayable)}</p>
          <p className="text-xs text-white/70 mt-1">
            Net payable · {lineItems.length} employees
          </p>
          <div className="grid grid-cols-3 gap-2 mt-4">
            <MiniStat label="OT pay" value={formatCurrency(totalOt)} />
            <MiniStat label="Additions" value={formatCurrency(totalAdditions)} />
            <MiniStat label="Deductions" value={formatCurrency(totalDeductions)} />
          </div>
        </div>
      </Card>

      {/* Progress */}
      <Card className="bg-porcelain shadow-sm p-4">
        <div className="flex items-center justify-between mb-2">
          <span className="text-sm font-medium text-graphite">Payment progress</span>
          <span className="text-sm font-semibold text-graphite">
            {paidCount}/{lineItems.length}
          </span>
        </div>
        <div className="h-2 bg-muted rounded-full overflow-hidden">
          <div
            className="h-full bg-jungle-teal rounded-full transition-all"
            style={{ width: `${lineItems.length ? (paidCount / lineItems.length) * 100 : 0}%` }}
          />
        </div>
        <div className="flex gap-2 mt-3">
          {run.status !== "paid" && (
            <>
              {run.status === "draft" && (
                <Button
                  variant="outline"
                  size="sm"
                  className="flex-1 h-9"
                  onClick={() => finalizeMutation.mutate()}
                  disabled={finalizeMutation.isPending}
                >
                  <Stamp className="size-4" /> Finalize
                </Button>
              )}
              <PayAllDialog
                onConfirm={(via) => markAllPaidMutation.mutate(via)}
                disabled={markAllPaidMutation.isPending || allPaid}
              />
            </>
          )}
          {allPaid && (
            <div className="flex-1 flex items-center justify-center gap-1.5 text-emerald-700 text-sm font-medium py-1">
              <CheckCircle2 className="size-4" /> All salaries paid
            </div>
          )}
        </div>
      </Card>

      {/* Line items */}
      <div className="space-y-2">
        <div className="flex items-center justify-between px-1">
          <h2 className="text-sm font-semibold text-graphite/70 uppercase tracking-wide">
            Salary slips
          </h2>
          <Button
            variant="ghost"
            size="sm"
            className="h-7 text-xs text-graphite/60 hover:text-jungle-teal px-2"
            onClick={() => exportPayrollCSV(run, business?.name ?? "Business")}
          >
            <FileSpreadsheet className="size-3.5" /> Export CSV
          </Button>
        </div>
        {lineItems.map((item) => (
          <LineItemCard
            key={item.id}
            item={item}
            businessName={business?.name ?? ""}
            year={run.year}
            month={run.month}
            onMarkPaid={(via) => markPaidMutation.mutate({ lineItemId: item.id, paidVia: via })}
            mutating={markPaidMutation.isPending || markAllPaidMutation.isPending}
          />
        ))}
      </div>
    </div>
  );
}

function MiniStat({ label, value }: { label: string; value: string }) {
  return (
    <div className="bg-white/15 rounded-lg py-1.5 px-2">
      <p className="text-[10px] text-white/70">{label}</p>
      <p className="text-sm font-semibold leading-tight">{value}</p>
    </div>
  );
}

function StatusPill({ status }: { status: string }) {
  const map: Record<string, string> = {
    draft: "bg-amber-400/30 text-amber-50",
    finalized: "bg-sky-400/30 text-sky-50",
    paid: "bg-emerald-400/30 text-emerald-50",
  };
  return (
    <span className={cn("text-[10px] px-2 py-0.5 rounded-full font-medium capitalize", map[status] ?? map.draft)}>
      {status}
    </span>
  );
}

function LineItemCard({
  item,
  businessName,
  year,
  month,
  onMarkPaid,
  mutating,
}: {
  item: PayrollLineItemShape;
  businessName: string;
  year: number;
  month: number;
  onMarkPaid: (via: string) => void;
  mutating: boolean;
}) {
  const [open, setOpen] = React.useState(false);
  const [payOpen, setPayOpen] = React.useState(false);
  const [payVia, setPayVia] = React.useState("cash");
  const isPaid = item.status === "paid";

  const handleDownload = () => {
    openSalarySlipPrint({
      business: { name: businessName},
      employee: {
        name: item.employeeName,
        phone: "",
        designation: null,
        salaryType: item.salaryType,
      },
      item,
      year,
      month,
    });
  };

  return (
    <Card className={cn("bg-porcelain shadow-sm overflow-hidden", isPaid && "opacity-75")}>
      <Collapsible open={open} onOpenChange={setOpen}>
        <CollapsibleTrigger asChild>
          <button className="w-full text-left p-3.5">
            <div className="flex items-center gap-3">
              <div className="size-10 rounded-full bg-accent flex items-center justify-center text-jungle-teal font-semibold text-sm shrink-0">
                {item.employeeName.slice(0, 2).toUpperCase()}
              </div>
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2">
                  <p className="text-sm font-medium text-graphite truncate">{item.employeeName}</p>
                  {isPaid && (
                    <Badge className="bg-emerald-100 text-emerald-700 hover:bg-emerald-100 text-[9px] h-4 px-1.5">
                      <CheckCircle2 className="size-2.5 mr-0.5" /> Paid
                    </Badge>
                  )}
                </div>
                <p className="text-[11px] text-graphite/55">
                  {item.presentDays}P · {item.halfDays}H · {item.paidLeaveDays}PL
                  {item.overtimeHours > 0 && ` · ${item.overtimeHours}h OT`}
                </p>
              </div>
              <div className="text-right shrink-0">
                <p className="text-sm font-bold text-graphite">{formatCurrency(item.netPayable)}</p>
                <p className="text-[10px] text-graphite/45">net pay</p>
              </div>
              <ChevronDown className={cn("size-4 text-graphite/40 shrink-0 transition-transform", open && "rotate-180")} />
            </div>
          </button>
        </CollapsibleTrigger>
        <CollapsibleContent>
          <div className="px-3.5 pb-3.5 pt-1 space-y-2 border-t border-border/40">
            {/* Breakdown */}
            <div className="space-y-1.5 pt-2">
              <BreakRow icon={FileText} label="Earned salary" value={formatCurrency(item.earnedSalary)} />
              {item.overtimePay > 0 && (
                <BreakRow icon={Clock} label={`Overtime (${item.overtimeHours}h)`} value={formatCurrency(item.overtimePay)} positive />
              )}
              {item.totalAdditions > 0 && (
                <BreakRow icon={TrendingUp} label="Additions" value={`+ ${formatCurrency(item.totalAdditions)} positive`} />
              )}
              {item.totalDeductions > 0 && (
                <BreakRow icon={FileText} label="Deductions" value={`- ${formatCurrency(item.totalDeductions)}`} negative />
              )}
            </div>
            <div className="flex items-center justify-between pt-2 border-t border-border/40">
              <span className="text-sm font-semibold text-graphite">Net payable</span>
              <span className="text-base font-bold text-jungle-teal">{formatCurrency(item.netPayable)}</span>
            </div>

            {/* Attendance detail */}
            <div className="grid grid-cols-4 gap-1.5 pt-1">
              <DetBox label="Present" value={item.presentDays} />
              <DetBox label="Half" value={item.halfDays} />
              <DetBox label="Paid Lv" value={item.paidLeaveDays} />
              <DetBox label="Unpaid" value={item.unpaidLeaveDays} />
            </div>
            <div className="grid grid-cols-2 gap-1.5">
              <DetBox label="Paid holidays" value={item.holidayDays} />
              <DetBox label="OT hours" value={item.overtimeHours} />
            </div>

            {/* Pay action */}
            {!isPaid ? (
              <div className="flex gap-2 mt-2">
                <Dialog open={payOpen} onOpenChange={setPayOpen}>
                  <Button
                    className="flex-1 bg-jungle-teal hover:bg-jungle-teal/90 text-white h-9"
                    onClick={() => setPayOpen(true)}
                    disabled={mutating}
                  >
                    <Banknote className="size-4" /> Mark as paid
                  </Button>
                  <DialogContent className="max-w-md">
                    <DialogHeader>
                      <DialogTitle>Mark {item.employeeName} as paid</DialogTitle>
                    </DialogHeader>
                    <div className="space-y-4 py-2">
                      <div className="bg-accent/40 rounded-xl p-3 text-center">
                        <p className="text-xs text-graphite/55">Net payable</p>
                        <p className="text-2xl font-bold text-jungle-teal">{formatCurrency(item.netPayable)}</p>
                      </div>
                      <div className="space-y-1.5">
                        <label className="text-sm font-medium">Payment method</label>
                        <Select value={payVia} onValueChange={setPayVia}>
                          <SelectTrigger><SelectValue /></SelectTrigger>
                          <SelectContent>
                            <SelectItem value="cash"><span className="flex items-center gap-2"><Banknote className="size-4" /> Cash</span></SelectItem>
                            <SelectItem value="upi"><span className="flex items-center gap-2"><Smartphone className="size-4" /> UPI</span></SelectItem>
                            <SelectItem value="bank"><span className="flex items-center gap-2"><Building2 className="size-4" /> Bank transfer</span></SelectItem>
                          </SelectContent>
                        </Select>
                      </div>
                    </div>
                    <DialogFooter>
                      <DialogClose asChild><Button variant="outline">Cancel</Button></DialogClose>
                      <Button
                        className="bg-jungle-teal hover:bg-jungle-teal/90 text-white"
                        onClick={() => { onMarkPaid(payVia); setPayOpen(false); }}
                        disabled={mutating}
                      >
                        Confirm payment
                      </Button>
                    </DialogFooter>
                  </DialogContent>
                </Dialog>
                <Button
                  variant="outline"
                  size="sm"
                  className="h-9 px-3"
                  onClick={handleDownload}
                  title="Download slip (PDF)"
                >
                  <Download className="size-4" />
                </Button>
              </div>
            ) : (
              <div className="flex items-center gap-2 mt-2">
                <div className="flex-1 flex items-center justify-center gap-1.5 text-emerald-700 text-sm font-medium py-1">
                  <CheckCircle2 className="size-4" />
                  Paid via {item.paidVia} {item.paidDate && `on ${formatDate(item.paidDate)}`}
                </div>
                <Button
                  variant="outline"
                  size="sm"
                  className="h-9 px-3 shrink-0"
                  onClick={handleDownload}
                  title="Download slip (PDF)"
                >
                  <Download className="size-4" />
                </Button>
              </div>
            )}
          </div>
        </CollapsibleContent>
      </Collapsible>
    </Card>
  );
}

function BreakRow({
  icon: Icon,
  label,
  value,
  positive,
  negative,
}: {
  icon: React.ElementType;
  label: string;
  value: string;
  positive?: boolean;
  negative?: boolean;
}) {
  return (
    <div className="flex items-center justify-between text-xs">
      <span className="text-graphite/60 flex items-center gap-1.5">
        <Icon className={cn("size-3.5", positive && "text-emerald-600", negative && "text-rose-600", !positive && !negative && "text-graphite/40")} />
        {label}
      </span>
      <span className={cn("font-medium", positive && "text-emerald-700", negative && "text-rose-700", !positive && !negative && "text-graphite")}>
        {value}
      </span>
    </div>
  );
}

function DetBox({ label, value }: { label: string; value: number }) {
  return (
    <div className="bg-muted rounded-lg py-1.5 text-center">
      <p className="text-sm font-bold text-graphite leading-tight">{value}</p>
      <p className="text-[9px] text-graphite/50">{label}</p>
    </div>
  );
}

function PayAllDialog({
  onConfirm,
  disabled,
}: {
  onConfirm: (via: string) => void;
  disabled: boolean;
}) {
  const [open, setOpen] = React.useState(false);
  const [via, setVia] = React.useState("cash");
  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        <Button size="sm" className="flex-1 h-9 bg-jungle-teal hover:bg-jungle-teal/90 text-white" disabled={disabled}>
          <CheckCheck className="size-4" /> Mark all paid
        </Button>
      </DialogTrigger>
      <DialogContent className="max-w-md">
        <DialogHeader>
          <DialogTitle>Mark all as paid?</DialogTitle>
        </DialogHeader>
        <div className="space-y-4 py-2">
          <p className="text-sm text-graphite/60">
            This will mark all unpaid salary slips as paid using the selected method.
          </p>
          <div className="space-y-1.5">
            <label className="text-sm font-medium">Payment method for all</label>
            <Select value={via} onValueChange={setVia}>
              <SelectTrigger><SelectValue /></SelectTrigger>
              <SelectContent>
                <SelectItem value="cash">Cash</SelectItem>
                <SelectItem value="upi">UPI</SelectItem>
                <SelectItem value="bank">Bank transfer</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </div>
        <DialogFooter>
          <DialogClose asChild><Button variant="outline">Cancel</Button></DialogClose>
          <Button
            className="bg-jungle-teal hover:bg-jungle-teal/90 text-white"
            onClick={() => { onConfirm(via); setOpen(false); }}
          >
            <CheckCheck className="size-4" /> Confirm all paid
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
