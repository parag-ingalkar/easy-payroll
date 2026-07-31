"use client";

import * as React from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { toast } from "sonner";
import {
  UserPlus,
  Phone,
  Briefcase,
  Search,
  ChevronRight,
  Users,
  Check,
} from "lucide-react";
import { apiFetch } from "@/lib/api";
import { useAuth } from "@/lib/auth-context";
import { useAppStore } from "@/store/app-store";
import { formatCurrency, SALARY_TYPE_LABELS, WEEKDAYS } from "@/lib/format";
import type { EmployeeShape } from "@/lib/types";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { ToggleGroup, ToggleGroupItem } from "@/components/ui/toggle-group";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
  DialogFooter,
  DialogClose,
} from "@/components/ui/dialog";

const employeeSchema = z.object({
  name: z.string().min(2, "Name is required"),
  phone: z.string().optional(),
  designation: z.string().optional(),
  salaryType: z.enum(["monthly", "daily", "hourly"]),
  baseRate: z.number().min(0, "Must be positive"),
  overtimeMultiplier: z.preprocess(
    (v) => (v === "" || v === null || v === undefined ? undefined : Number(v)),
    z.number().min(1).optional()
  ),
  workingHours: z.number().int().min(1).max(24),
  weeklyOffDays: z.array(z.string()),
});

type EmployeeValues = z.infer<typeof employeeSchema>;

export function EmployeesView() {
  const navigate = useAppStore((s) => s.navigate);
  const { business } = useAuth();
  const queryClient = useQueryClient();
  const [search, setSearch] = React.useState("");
  const [dialogOpen, setDialogOpen] = React.useState(false);
  const [created, setCreated] = React.useState<string | null>(null);

  const { data: employees, isLoading } = useQuery({
    queryKey: ["employees", business?.id],
    queryFn: () =>
      apiFetch<EmployeeShape[]>(
        `/api/business/${business!.id}/employees?include_inactive=true`,
      ),
    enabled: !!business?.id,
  });

  const {
    register,
    handleSubmit,
    setValue,
    watch,
    reset,
    formState: { errors },
  } = useForm<EmployeeValues>({
    resolver: zodResolver(employeeSchema),
    defaultValues: {
      name: "",
      phone: "",
      designation: "",
      salaryType: "monthly",
      baseRate: 0,
      workingHours: 8,
      weeklyOffDays: [],
    },
  });

  const createMutation = useMutation({
    mutationFn: (values: EmployeeValues) =>
      apiFetch<EmployeeShape>(`/api/business/${business!.id}/employees`, {
        method: "POST",
        body: JSON.stringify(values),
      }),
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ["employees", business?.id] });
      queryClient.invalidateQueries({ queryKey: ["dashboard"] });
      setCreated(data.name);
      reset();
    },
    onError: (err) => toast.error(err instanceof Error ? err.message : "Failed to add employee"),
  });

  const offDays = watch("weeklyOffDays") ?? [];

  const filtered = (employees ?? []).filter(
    (e) =>
      e.name.toLowerCase().includes(search.toLowerCase()) ||
      (e.phone ?? "").includes(search) ||
      (e.designation ?? "").toLowerCase().includes(search.toLowerCase())
  );

  const activeCount = filtered.filter((e) => e.isActive).length;

  return (
    <div className="space-y-4 pp-animate-in">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold text-graphite">Staff</h1>
          <p className="text-xs text-graphite/55">
            {activeCount} active · {filtered.length} total
          </p>
        </div>
        <Dialog open={dialogOpen} onOpenChange={(o) => { setDialogOpen(o); if (!o) setCreated(null); }}>
          <DialogTrigger asChild>
            <Button size="sm" className="bg-jungle-teal hover:bg-jungle-teal/90 text-white h-9">
              <UserPlus className="size-4" /> Add
            </Button>
          </DialogTrigger>
          <DialogContent className="max-w-md max-h-[90vh] overflow-y-auto scroll-area-thin">
            {created ? (
              <div className="py-2">
                <div className="flex flex-col items-center text-center mb-5">
                  <div className="size-14 rounded-2xl bg-emerald-100 flex items-center justify-center">
                    <Check className="size-7 text-emerald-600" />
                  </div>
                  <h2 className="text-lg font-semibold text-graphite mt-3">
                    {created} added!
                  </h2>
                  <p className="text-sm text-graphite/55 mt-1">
                    Employee has been added to your staff.
                  </p>
                </div>
                <Button
                  className="w-full mt-2 bg-jungle-teal hover:bg-jungle-teal/90 text-white"
                  onClick={() => { setDialogOpen(false); setCreated(null); }}
                >
                  Done
                </Button>
              </div>
            ) : (
              <>
                <DialogHeader>
                  <DialogTitle>Add employee</DialogTitle>
                </DialogHeader>
                <form
                  onSubmit={handleSubmit((v) => createMutation.mutate(v))}
                  className="space-y-4 py-2"
                >
                  <div className="space-y-1.5">
                    <Label>Full name *</Label>
                    <Input placeholder="e.g. Ravi Kumar" {...register("name")} />
                    {errors.name && <p className="text-xs text-destructive">{errors.name.message}</p>}
                  </div>
                  <div className="space-y-1.5">
                    <Label>Phone number</Label>
                    <div className="relative">
                      <Phone className="absolute left-3 top-1/2 -translate-y-1/2 size-4 text-graphite/40" />
                      <Input className="pl-9" placeholder="9876543210" {...register("phone")} />
                    </div>
                  </div>
                  <div className="space-y-1.5">
                    <Label>Designation</Label>
                    <div className="relative">
                      <Briefcase className="absolute left-3 top-1/2 -translate-y-1/2 size-4 text-graphite/40" />
                      <Input className="pl-9" placeholder="e.g. Sales Executive" {...register("designation")} />
                    </div>
                  </div>
                  <div className="space-y-1.5">
                    <Label>Salary type</Label>
                    <Select
                      value={watch("salaryType")}
                      onValueChange={(v) => setValue("salaryType", v as "monthly" | "daily" | "hourly")}
                    >
                      <SelectTrigger><SelectValue /></SelectTrigger>
                      <SelectContent>
                        <SelectItem value="monthly">Monthly Salary</SelectItem>
                        <SelectItem value="daily">Daily Wage</SelectItem>
                        <SelectItem value="hourly">Hourly Wage</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  <div className="grid grid-cols-2 gap-3">
                    <div className="space-y-1.5">
                      <Label>Base rate</Label>
                      <Input type="number" step="0.01" {...register("baseRate", { valueAsNumber: true })} />
                      {errors.baseRate && <p className="text-xs text-destructive">{errors.baseRate.message}</p>}
                    </div>
                    <div className="space-y-1.5">
                      <Label>Working hrs/day</Label>
                      <Input type="number" {...register("workingHours", { valueAsNumber: true })} />
                    </div>
                  </div>
                  <div className="space-y-1.5">
                    <Label>OT multiplier (optional)</Label>
                    <Input type="number" step="0.1" placeholder="1.5" {...register("overtimeMultiplier")} />
                  </div>
                  <div className="space-y-2">
                    <Label>Weekly off days</Label>
                    <ToggleGroup
                      type="multiple"
                      variant="outline"
                      className="flex flex-wrap justify-start gap-2"
                      value={offDays}
                      onValueChange={(val) => setValue("weeklyOffDays", val)}
                    >
                      {WEEKDAYS.map((d) => (
                        <ToggleGroupItem
                          key={d}
                          value={d}
                          className="data-[state=on]:bg-jungle-teal data-[state=on]:text-white text-xs h-8 px-3"
                        >
                          {d.slice(0, 3)}
                        </ToggleGroupItem>
                      ))}
                    </ToggleGroup>
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
                      {createMutation.isPending ? "Adding…" : "Add employee"}
                    </Button>
                  </DialogFooter>
                </form>
              </>
            )}
          </DialogContent>
        </Dialog>
      </div>

      {/* Search */}
      <div className="relative">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 size-4 text-graphite/40" />
        <Input
          className="pl-9 bg-porcelain"
          placeholder="Search by name, phone or role…"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />
      </div>

      {/* List */}
      {isLoading ? (
        <div className="space-y-2.5">
          {[0, 1, 2, 3].map((i) => (
            <div key={i} className="h-20 bg-graphite/10 rounded-2xl animate-pulse" />
          ))}
        </div>
      ) : filtered.length === 0 ? (
        <Card className="p-8 text-center bg-porcelain">
          <div className="size-14 rounded-2xl bg-accent flex items-center justify-center mx-auto">
            <Users className="size-7 text-jungle-teal" />
          </div>
          <p className="text-sm font-medium text-graphite mt-3">
            {search ? "No employees match your search" : "No employees yet"}
          </p>
          <p className="text-xs text-graphite/55 mt-1">
            {search ? "Try a different term." : "Add your first employee to get started."}
          </p>
        </Card>
      ) : (
        <div className="space-y-2.5">
          {filtered.map((emp) => (
            <button
              key={emp.id}
              onClick={() => navigate("employee-detail", { id: emp.id })}
              className="w-full text-left bg-porcelain rounded-2xl border border-border/60 p-3.5 shadow-sm hover:shadow-md hover:border-jungle-teal/25 transition-all active:scale-[0.99]"
            >
              <div className="flex items-center gap-3">
                <div className="size-10 rounded-full bg-accent flex items-center justify-center text-jungle-teal font-semibold text-sm shrink-0">
                  {emp.name.slice(0, 2).toUpperCase()}
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-[13px] font-semibold text-graphite truncate leading-tight">{emp.name}</p>
                  <p className="text-[11px] text-graphite/55 truncate mt-0.5">
                    {emp.designation || SALARY_TYPE_LABELS[emp.salaryType as "monthly" | "daily" | "hourly"]}
                  </p>
                </div>
                <div className="text-right shrink-0">
                  <p className="text-[13px] font-semibold text-graphite tabular-nums leading-tight">
                    {formatCurrency(emp.baseRate)}
                  </p>
                  <p className="text-[10px] text-graphite/45 mt-0.5">
                    {emp.salaryType === "monthly" ? "per month" : emp.salaryType === "daily" ? "per day" : "per hour"}
                  </p>
                </div>
              </div>
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
