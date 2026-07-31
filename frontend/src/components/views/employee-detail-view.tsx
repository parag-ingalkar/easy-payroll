"use client";

import * as React from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useForm, useWatch } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { toast } from "sonner";
import {
  ArrowLeft,
  Phone,
  Briefcase,
  Wallet,
  Calendar,
  Plus,
  TrendingUp,
  Banknote,
  Pencil,
} from "lucide-react";
import { apiFetch } from "@/lib/api";
import { useAuth } from "@/lib/auth-context";
import { useAppStore } from "@/store/app-store";
import {
  formatCurrency,
  formatDate,
  SALARY_TYPE_LABELS,
  ATTENDANCE_META,
  TRANSACTION_META,
  WEEKDAYS,
} from "@/lib/format";
import type {
  EmployeeShape,
  AttendanceShape,
  TransactionShape,
} from "@/lib/types";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
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
  DialogTrigger,
  DialogFooter,
  DialogClose,
} from "@/components/ui/dialog";
import { cn } from "@/lib/utils";

export function EmployeeDetailView({ employeeId }: { employeeId: string }) {
  const navigate = useAppStore((s) => s.navigate);
  const { business } = useAuth();
  
  const queryClient = useQueryClient();

  const { data: emp, isLoading } = useQuery({
    queryKey: ["employee", employeeId],
    queryFn: () => apiFetch<EmployeeShape>(`/api/employees/${employeeId}`),
    enabled: !!employeeId,
  });

  const { data: attendance } = useQuery({
    queryKey: ["employee-attendance", employeeId],
    queryFn: () =>
      apiFetch<AttendanceShape[]>(
        `/api/business/${business!.id}/employees/${employeeId}/attendances`,
      ),
    enabled: !!business?.id && !!employeeId,
  });

  const { data: transactions } = useQuery({
    queryKey: ["employee-transactions", employeeId],
    queryFn: () =>
      apiFetch<TransactionShape[]>(
        `/api/business/${business!.id}/employees/${employeeId}/transactions`,
      ),
    enabled: !!business?.id && !!employeeId,
  });

  if (isLoading || !emp) {
    return (
      <div className="space-y-4">
        <button
          onClick={() => navigate("employees")}
          className="flex items-center gap-1 text-sm text-graphite/60"
        >
          <ArrowLeft className="size-4" /> Back
        </button>
        <div className="h-40 bg-graphite/10 rounded-2xl animate-pulse" />
      </div>
    );
  }

  return (
    <div className="space-y-4 pp-animate-in">
      <button
        onClick={() => navigate("employees")}
        className="flex items-center gap-1 text-sm text-graphite/60 hover:text-graphite"
      >
        <ArrowLeft className="size-4" /> Staff
      </button>

      {/* Profile header */}
      <Card className="bg-porcelain shadow-sm p-4">
        <div className="flex items-start gap-3">
          <div className="size-12 rounded-full bg-accent flex items-center justify-center text-jungle-teal font-bold text-base shrink-0">
            {emp.name.slice(0, 2).toUpperCase()}
          </div>
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2">
              <h1 className="text-lg font-bold text-graphite leading-tight truncate">
                {emp.name}
              </h1>
              {!emp.isActive && (
                <Badge variant="secondary" className="text-[9px] h-4 px-1.5">
                  Inactive
                </Badge>
              )}
            </div>
            <p className="text-sm text-graphite/55 mt-0.5">
              {emp.designation || "No designation"}
            </p>
          </div>
          <EditEmployeeDialog employee={emp} />
        </div>

        <div className="grid grid-cols-3 gap-2 mt-4 pt-4 border-t border-border/40">
          <div>
            <p className="text-sm font-semibold text-graphite tabular-nums">
              {formatCurrency(emp.baseRate)}
            </p>
            <p className="text-[10px] text-graphite/55">
              {emp.salaryType === "monthly"
                ? "per month"
                : emp.salaryType === "daily"
                  ? "per day"
                  : "per hour"}
            </p>
          </div>
          <div>
            <p className="text-sm font-semibold text-graphite tabular-nums">
              {emp.workingHours}h
            </p>
            <p className="text-[10px] text-graphite/55">per day</p>
          </div>
          <div>
            <p className="text-sm font-semibold text-graphite tabular-nums">
              {emp.overtimeMultiplier ??
                business?.defaultOvertimeMultiplier ??
                1.5}
              ×
            </p>
            <p className="text-[10px] text-graphite/55">OT rate</p>
          </div>
        </div>

        <div className="flex items-center gap-2 mt-3 text-[11px] text-graphite/55">
          {emp.phone && (
            <>
              <Phone className="size-3.5" /> {emp.phone}
              {emp.joiningDate && (
                <>
                  <span className="text-graphite/30">·</span>
                  <Calendar className="size-3.5" />
                  Joined{" "}
                  {formatDate(emp.joiningDate, {
                    month: "short",
                    year: "numeric",
                  })}
                </>
              )}
            </>
          )}
        </div>
      </Card>

      {/* Tabs */}
      <Tabs defaultValue="overview">
        <TabsList className="grid grid-cols-3 w-full">
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="attendance">Attendance</TabsTrigger>
          <TabsTrigger value="money">Money</TabsTrigger>
        </TabsList>

        <TabsContent value="overview" className="mt-4 space-y-3">
          <OverviewTab
            emp={emp}
            attendance={attendance ?? []}
            transactions={transactions ?? []}
          />
        </TabsContent>

        <TabsContent value="attendance" className="mt-4">
          <AttendanceTab records={attendance ?? []} />
        </TabsContent>

        <TabsContent value="money" className="mt-4">
          <TransactionsTab
            employeeId={emp.id}
            transactions={transactions ?? []}
          />
        </TabsContent>
      </Tabs>
    </div>
  );
}

function OverviewTab({
  emp,
  attendance,
  transactions,
}: {
  emp: EmployeeShape;
  attendance: AttendanceShape[];
  transactions: TransactionShape[];
}) {
  const now = new Date();
  const monthRecords = attendance.filter((a) => {
    const d = new Date(a.date);
    return (
      d.getMonth() === now.getMonth() && d.getFullYear() === now.getFullYear()
    );
  });
  const present = monthRecords.filter((a) => a.status === "present").length;
  const half = monthRecords.filter((a) => a.status === "half_day").length;
  const pl = monthRecords.filter((a) => a.status === "paid_leave").length;
  const ul = monthRecords.filter((a) => a.status === "unpaid_leave").length;
  const ot = monthRecords.reduce((s, a) => s + (a.overtimeHours || 0), 0);

  const monthTx = transactions.filter((t) => {
    const d = new Date(t.transactionDate);
    return (
      d.getMonth() === now.getMonth() && d.getFullYear() === now.getFullYear()
    );
  });
  const additions = monthTx
    .filter((t) => t.type === "addition")
    .reduce((s, t) => s + t.amount, 0);
  const deductions = monthTx
    .filter((t) => t.type === "deduction")
    .reduce((s, t) => s + t.amount, 0);

  const offDays = Array.isArray(emp.weeklyOffDays) ? emp.weeklyOffDays : [];

  return (
    <>
      <Card className="bg-porcelain shadow-sm p-4">
        <p className="text-[11px] font-medium text-graphite/55 mb-3">
          {now.toLocaleDateString("en-IN", { month: "long" })} attendance
        </p>
        <div className="flex items-baseline gap-2 mb-3">
          <span className="text-2xl font-bold text-graphite tabular-nums leading-none">
            {present}
          </span>
          <span className="text-xs text-graphite/55">days present</span>
          {ot > 0 && (
            <span className="ml-auto text-xs text-graphite/55">
              <span className="font-semibold text-graphite tabular-nums">
                {ot}h
              </span>{" "}
              overtime
            </span>
          )}
        </div>
        <div className="flex flex-wrap gap-x-4 gap-y-1 text-[11px] text-graphite/60">
          <span>
            <span className="font-semibold text-graphite tabular-nums">
              {half}
            </span>{" "}
            half days
          </span>
          <span>
            <span className="font-semibold text-graphite tabular-nums">
              {pl}
            </span>{" "}
            paid leave
          </span>
          <span>
            <span className="font-semibold text-graphite tabular-nums">
              {ul}
            </span>{" "}
            unpaid
          </span>
        </div>
      </Card>

      <Card className="bg-porcelain shadow-sm p-4">
        <p className="text-[11px] font-medium text-graphite/55 mb-3">
          {now.toLocaleDateString("en-IN", { month: "long" })} transactions
        </p>
        <div className="space-y-2">
          <Row
            label="Additions"
            value={formatCurrency(additions)}
            color="text-emerald-700"
            icon={TrendingUp}
          />
          <Row
            label="Deductions"
            value={formatCurrency(deductions)}
            color="text-rose-700"
            icon={Banknote}
          />
        </div>
      </Card>

      <Card className="bg-porcelain shadow-sm p-4">
        <p className="text-xs font-medium text-graphite/50 uppercase tracking-wide mb-2">
          Weekly off days
        </p>
        <div className="flex flex-wrap gap-1.5">
          {WEEKDAYS.map((d) => (
            <Badge
              key={d}
              variant="outline"
              className={cn(
                "text-xs",
                offDays.includes(d)
                  ? "bg-jungle-teal text-white border-jungle-teal"
                  : "text-graphite/40",
              )}
            >
              {d.slice(0, 3)}
            </Badge>
          ))}
        </div>
      </Card>
    </>
  );
}

function Row({
  label,
  value,
  color,
  icon: Icon,
}: {
  label: string;
  value: string;
  color: string;
  icon: React.ElementType;
}) {
  return (
    <div className="flex items-center justify-between">
      <span className="text-sm text-graphite/60 flex items-center gap-1.5">
        <Icon className={cn("size-3.5", color)} /> {label}
      </span>
      <span className={cn("text-sm font-semibold", color)}>{value}</span>
    </div>
  );
}

function AttendanceTab({ records }: { records: AttendanceShape[] }) {
  if (records.length === 0) {
    return (
      <Card className="p-8 text-center bg-porcelain">
        <Calendar className="size-8 text-graphite/30 mx-auto" />
        <p className="text-sm text-graphite/55 mt-2">
          No attendance records yet.
        </p>
      </Card>
    );
  }
  return (
    <div className="space-y-2 max-h-[60vh] overflow-y-auto scroll-area-thin pr-1">
      {records.map((r) => {
        const meta = ATTENDANCE_META[r.status as keyof typeof ATTENDANCE_META];
        return (
          <Card key={r.id} className="bg-porcelain shadow-sm p-3">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div
                  className={cn(
                    "size-10 rounded-xl flex flex-col items-center justify-center",
                    meta.bg,
                    meta.color,
                  )}
                >
                  <span className="text-sm font-bold leading-none">
                    {new Date(r.date).getDate()}
                  </span>
                  <span className="text-[8px] uppercase">
                    {formatDate(r.date, { month: "short" })}
                  </span>
                </div>
                <div>
                  <p className={cn("text-sm font-medium", meta.color)}>
                    {meta.label}
                  </p>
                  <p className="text-[11px] text-graphite/50">
                    {formatDate(r.date, { weekday: "long" })}
                    {r.overtimeHours > 0 && ` · ${r.overtimeHours}h OT`}
                  </p>
                </div>
              </div>
              <span
                className={cn(
                  "text-xs font-bold px-2 py-1 rounded-lg",
                  meta.bg,
                  meta.color,
                )}
              >
                {meta.short}
              </span>
            </div>
          </Card>
        );
      })}
    </div>
  );
}

const txSchema = z.object({
  type: z.enum(["addition", "deduction"]),
  amount: z.number().min(0.01, "Amount required"),
  description: z.string().optional(),
  transactionDate: z.string().optional(),
});

type TxValues = z.infer<typeof txSchema>;

function TransactionsTab({
  employeeId,
  transactions,
}: {
  employeeId: string;
  transactions: TransactionShape[];
}) {
  const { business } = useAuth();
  const queryClient = useQueryClient();
  const [open, setOpen] = React.useState(false);
  const {
    register,
    handleSubmit,
    setValue,
    watch,
    reset,
    formState: { errors },
  } = useForm<TxValues>({
    resolver: zodResolver(txSchema),
    defaultValues: { type: "addition", amount: 0, transactionDate: ymdToday() },
  });

  const createMutation = useMutation({
    mutationFn: (v: TxValues) =>
      apiFetch(
        `/api/business/${business!.id}/employees/${employeeId}/transactions`,
        {
          method: "POST",
          body: JSON.stringify(v),
        },
      ),
    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: ["employee-transactions", employeeId],
      });
      queryClient.invalidateQueries({ queryKey: ["dashboard"] });
      toast.success("Transaction added");
      setOpen(false);
      reset({ type: "addition", amount: 0, transactionDate: ymdToday() });
    },
    onError: (err) =>
      toast.error(err instanceof Error ? err.message : "Failed"),
  });

  const deleteMutation = useMutation({
    mutationFn: (txId: string) =>
      apiFetch(
        `/api/business/${business!.id}/employees/${employeeId}/transactions/${txId}`,
        { method: "DELETE" },
      ),
    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: ["employee-transactions", employeeId],
      });
      queryClient.invalidateQueries({ queryKey: ["dashboard"] });
      toast.success("Transaction removed");
    },
    onError: (err) =>
      toast.error(err instanceof Error ? err.message : "Failed"),
  });

  const type = watch("type");

  return (
    <div className="space-y-3">
      <Dialog open={open} onOpenChange={setOpen}>
        <DialogTrigger asChild>
          <Button className="w-full bg-jungle-teal hover:bg-jungle-teal/90 text-white h-11">
            <Plus className="size-4" /> Add transaction
          </Button>
        </DialogTrigger>
        <DialogContent className="max-w-md">
          <DialogHeader>
            <DialogTitle>Add transaction</DialogTitle>
          </DialogHeader>
          <form
            onSubmit={handleSubmit((v) => createMutation.mutate(v))}
            className="space-y-4 py-2"
          >
            <div className="space-y-1.5">
              <Label>Type</Label>
              <Select
                value={type}
                onValueChange={(v) =>
                  setValue("type", v as "addition" | "deduction")
                }
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="addition">
                    Addition (added to salary)
                  </SelectItem>
                  <SelectItem value="deduction">Deduction</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div className="space-y-1.5">
              <Label>Amount </Label>
              <Input
                type="number"
                step="0.01"
                {...register("amount", { valueAsNumber: true })}
              />
              {errors.amount && (
                <p className="text-xs text-destructive">
                  {errors.amount.message}
                </p>
              )}
            </div>
            <div className="space-y-1.5">
              <Label>Description (optional)</Label>
              <Input
                placeholder="e.g. Festival bonus"
                {...register("description")}
              />
            </div>
            <div className="space-y-1.5">
              <Label>Date</Label>
              <Input type="date" {...register("transactionDate")} />
            </div>
            <DialogFooter>
              <DialogClose asChild>
                <Button variant="outline">Cancel</Button>
              </DialogClose>
              <Button
                type="submit"
                className="bg-jungle-teal hover:bg-jungle-teal/90 text-white"
                disabled={createMutation.isPending}
              >
                {createMutation.isPending ? "Adding…" : "Add"}
              </Button>
            </DialogFooter>
          </form>
        </DialogContent>
      </Dialog>

      {transactions.length === 0 ? (
        <Card className="p-8 text-center bg-porcelain">
          <Wallet className="size-8 text-graphite/30 mx-auto" />
          <p className="text-sm text-graphite/55 mt-2">No transactions yet.</p>
        </Card>
      ) : (
        <div className="space-y-2 max-h-[55vh] overflow-y-auto scroll-area-thin pr-1">
          {transactions.map((t) => {
            const meta =
              TRANSACTION_META[t.type as keyof typeof TRANSACTION_META];
            return (
              <Card key={t.id} className="bg-porcelain shadow-sm p-3">
                <div className="flex items-center gap-3">
                  <div
                    className={cn(
                      "size-10 rounded-xl flex items-center justify-center",
                      meta.bg,
                      meta.color,
                    )}
                  >
                    {t.type === "addition" ? (
                      <TrendingUp className="size-5" />
                    ) : (
                      <Banknote className="size-5" />
                    )}
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className={cn("text-sm font-medium", meta.color)}>
                      {meta.label}
                    </p>
                    <p className="text-[11px] text-graphite/50">
                      {formatDate(t.transactionDate)}
                      {t.description && ` · ${t.description}`}
                    </p>
                  </div>
                  <p className={cn("text-sm font-bold", meta.color)}>
                    {meta.sign}
                    {formatCurrency(t.amount)}
                  </p>
                  <button
                    onClick={() => deleteMutation.mutate(t.id)}
                    className="size-7 rounded-lg flex items-center justify-center text-graphite/30 hover:text-destructive hover:bg-destructive/10 opacity-0 group-hover:opacity-100 transition-opacity shrink-0"
                  >
                    {/* trash icon handled via hover — simple delete */}
                  </button>
                </div>
              </Card>
            );
          })}
        </div>
      )}
    </div>
  );
}

function EditEmployeeDialog({ employee }: { employee: EmployeeShape }) {
  const queryClient = useQueryClient();
  const [open, setOpen] = React.useState(false);
  const { register, handleSubmit, setValue, watch, reset, control } = useForm({
    defaultValues: {
      name: employee.name,
      designation: employee.designation ?? "",
      salaryType: employee.salaryType,
      baseRate: employee.baseRate,
      overtimeMultiplier: employee.overtimeMultiplier ?? 1.5,
      workingHours: employee.workingHours,
      isActive: employee.isActive,
    },
  });
  const salaryType = useWatch({ control, name: "salaryType" });
  const isActive = useWatch({ control, name: "isActive" });

  React.useEffect(() => {
    reset({
      name: employee.name,
      designation: employee.designation ?? "",
      salaryType: employee.salaryType,
      baseRate: employee.baseRate,
      overtimeMultiplier: employee.overtimeMultiplier ?? 1.5,
      workingHours: employee.workingHours,
      isActive: employee.isActive,
    });
  }, [employee, reset]);

  const mutation = useMutation({
    mutationFn: (v: Record<string, unknown>) =>
      apiFetch(`/api/employees/${employee.id}`, {
        method: "PATCH",
        body: JSON.stringify(v),
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["employee", employee.id] });
      queryClient.invalidateQueries({ queryKey: ["employees"] });
      toast.success("Employee updated");
      setOpen(false);
    },
    onError: (err) =>
      toast.error(err instanceof Error ? err.message : "Failed"),
  });

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        <Button size="sm" variant="outline" className="h-8">
          <Pencil className="size-3.5" /> Edit
        </Button>
      </DialogTrigger>
      <DialogContent className="max-w-md max-h-[90vh] overflow-y-auto scroll-area-thin">
        <DialogHeader>
          <DialogTitle>Edit employee</DialogTitle>
        </DialogHeader>
        <form
          onSubmit={handleSubmit((v) => mutation.mutate(v))}
          className="space-y-4 py-2"
        >
          <div className="space-y-1.5">
            <Label>Name</Label>
            <Input {...register("name")} />
          </div>
          <div className="space-y-1.5">
            <Label>Designation</Label>
            <Input {...register("designation")} />
          </div>
          <div className="space-y-1.5">
            <Label>Salary type</Label>
            <Select
              value={salaryType}
              onValueChange={(v) => setValue("salaryType", v)}
            >
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="monthly">Monthly</SelectItem>
                <SelectItem value="daily">Daily</SelectItem>
                <SelectItem value="hourly">Hourly</SelectItem>
              </SelectContent>
            </Select>
          </div>
          <div className="grid grid-cols-2 gap-3">
            <div className="space-y-1.5">
              <Label>Base rate </Label>
              <Input
                type="number"
                step="0.01"
                {...register("baseRate", { valueAsNumber: true })}
              />
            </div>
            <div className="space-y-1.5">
              <Label>Working hrs</Label>
              <Input
                type="number"
                {...register("workingHours", { valueAsNumber: true })}
              />
            </div>
          </div>
          <div className="grid grid-cols-2 gap-3">
            <div className="space-y-1.5">
              <Label>OT multiplier</Label>
              <Input
                type="number"
                step="0.1"
                {...register("overtimeMultiplier", { valueAsNumber: true })}
              />
            </div>
            <div className="space-y-1.5">
              <Label>Status</Label>
              <Select
                value={isActive ? "active" : "inactive"}
                onValueChange={(v) => setValue("isActive", v === "active")}
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="active">Active</SelectItem>
                  <SelectItem value="inactive">Inactive</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>
          <DialogFooter>
            <DialogClose asChild>
              <Button variant="outline">Cancel</Button>
            </DialogClose>
            <Button
              type="submit"
              className="bg-jungle-teal hover:bg-jungle-teal/90 text-white"
              disabled={mutation.isPending}
            >
              {mutation.isPending ? "Saving…" : "Save"}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}

function ymdToday(): string {
  const d = new Date();
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}-${String(d.getDate()).padStart(2, "0")}`;
}
