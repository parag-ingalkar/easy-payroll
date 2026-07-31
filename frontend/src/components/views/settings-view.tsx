"use client";

import * as React from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useForm, useWatch } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { toast } from "sonner";
import { Store, CalendarPlus, Trash2, Plane, Save, Plus, Sun, Moon, Palette } from "lucide-react";
import { useTheme } from "next-themes";
import { apiFetch } from "@/lib/api";
import { useAuth } from "@/lib/auth-context";
import { WEEKDAYS, formatDate, startOfDay } from "@/lib/format";
import type { BusinessShape, HolidayShape } from "@/lib/types";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Switch } from "@/components/ui/switch";
import { ToggleGroup, ToggleGroupItem } from "@/components/ui/toggle-group";
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

const settingsSchema = z.object({
  name: z.string().min(2, "Business name is required"),
  divisorPolicy: z.enum(["26", "30", "calendar"]),
  defaultOvertimeMultiplier: z.number().min(1).max(5),
  defaultWorkingHours: z.number().int().min(1).max(24),
  defaultWeeklyOffDays: z.array(z.string()),
});

type SettingsValues = z.infer<typeof settingsSchema>;

export function SettingsView() {
  const { business, refreshUser, user } = useAuth();
  const queryClient = useQueryClient();
  const [saving, setSaving] = React.useState(false);

  const { register, handleSubmit, setValue, reset, control } = useForm<SettingsValues>({
    resolver: zodResolver(settingsSchema),
    defaultValues: {
      name: "",
      divisorPolicy: "30",
      defaultOvertimeMultiplier: 1.5,
      defaultWorkingHours: 8,
      defaultWeeklyOffDays: ["Sunday"],
    },
  });
  const divisorPolicy = useWatch({ control, name: "divisorPolicy" });
  const offDays = useWatch({ control, name: "defaultWeeklyOffDays" }) ?? [];

  React.useEffect(() => {
    if (business) {
      reset({
        name: business.name,
        divisorPolicy: business.divisorPolicy as "26" | "30" | "calendar",
        defaultOvertimeMultiplier: business.defaultOvertimeMultiplier,
        defaultWorkingHours: business.defaultWorkingHours,
        defaultWeeklyOffDays: Array.isArray(business.defaultWeeklyOffDays)
          ? business.defaultWeeklyOffDays
          : [],
      });
    }
  }, [business, reset]);

  const onSave = async (values: SettingsValues) => {
    setSaving(true);
    try {
      await apiFetch<BusinessShape>(`/api/business/${business!.id}`, {
        method: "PATCH",
        body: JSON.stringify(values),
      });
      await refreshUser();
      queryClient.invalidateQueries({ queryKey: ["dashboard"] });
      toast.success("Settings saved");
    } catch (err) {
      toast.error(err instanceof Error ? err.message : "Failed to save");
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="space-y-5 pp-animate-in">
      <div>
        <h1 className="text-xl font-bold text-graphite">Settings</h1>
        <p className="text-xs text-graphite/55">Manage your business and account.</p>
      </div>

      {/* Business settings */}
      <Card className="bg-porcelain shadow-sm py-0 gap-0">
        <div className="px-4 pt-3.5 pb-3 flex items-center gap-2 border-b border-border/40">
          <div className="size-8 rounded-lg bg-accent flex items-center justify-center">
            <Store className="size-4 text-jungle-teal" />
          </div>
          <h2 className="text-sm font-semibold text-graphite">Business profile</h2>
        </div>
        <form onSubmit={handleSubmit(onSave)} className="p-4 space-y-4">
          <div className="space-y-1.5">
            <Label htmlFor="s-name">Business name</Label>
            <Input id="s-name" {...register("name")} />
          </div>
          <div className="grid grid-cols-2 gap-3">
            <div className="space-y-1.5">
              <Label htmlFor="s-ot">OT multiplier</Label>
              <Input id="s-ot" type="number" step="0.1" {...register("defaultOvertimeMultiplier", { valueAsNumber: true })} />
            </div>
            <div className="space-y-1.5">
              <Label htmlFor="s-hours">Working hrs/day</Label>
              <Input id="s-hours" type="number" {...register("defaultWorkingHours", { valueAsNumber: true })} />
            </div>
          </div>
          <div className="space-y-1.5">
            <Label>Divisor policy</Label>
            <Select
              value={divisorPolicy}
              onValueChange={(v) => setValue("divisorPolicy", v as "26" | "30" | "calendar")}
            >
              <SelectTrigger><SelectValue /></SelectTrigger>
              <SelectContent>
                <SelectItem value="30">30 days (standard)</SelectItem>
                <SelectItem value="26">26 days (working days)</SelectItem>
                <SelectItem value="calendar">Calendar days</SelectItem>
              </SelectContent>
            </Select>
          </div>
          <div className="space-y-2">
            <Label>Weekly off days</Label>
            <ToggleGroup
              type="multiple"
              variant="outline"
              className="flex flex-wrap justify-start"
              value={offDays}
              onValueChange={(val) => setValue("defaultWeeklyOffDays", val)}
            >
              {WEEKDAYS.map((d) => (
                <ToggleGroupItem
                  key={d}
                  value={d}
                  className="data-[state=on]:bg-jungle-teal data-[state=on]:text-white text-xs h-8 px-3"
                >
                  {d.slice(0, 3).toUpperCase()}
                </ToggleGroupItem>
              ))}
            </ToggleGroup>
          </div>
          <Button type="submit" className="w-full bg-jungle-teal hover:bg-jungle-teal/90 text-white h-11" disabled={saving}>
            <Save className="size-4" />
            {saving ? "Saving…" : "Save changes"}
          </Button>
        </form>
      </Card>

      {/* Holidays */}
      <HolidaysSection />

      {/* Appearance */}
      <AppearanceSection />

      {/* Account */}
      <Card className="bg-porcelain shadow-sm py-0 gap-0">
        <div className="px-4 pt-3.5 pb-3 flex items-center gap-2 border-b border-border/40">
          <div className="size-8 rounded-lg bg-accent flex items-center justify-center">
            <Plane className="size-4 text-jungle-teal" />
          </div>
          <h2 className="text-sm font-semibold text-graphite">Account</h2>
        </div>
        <div className="p-4 space-y-3">
          <div className="flex items-center justify-between">
            <span className="text-sm text-graphite/60">Email</span>
            <span className="text-sm font-medium text-graphite">{user?.email}</span>
          </div>
          <div className="flex items-center justify-between">
            <span className="text-sm text-graphite/60">Role</span>
            <span className="text-sm font-medium text-graphite capitalize">{user?.roles?.[0] ?? "—"}</span>
          </div>
        </div>
      </Card>

      <p className="text-center text-[11px] text-graphite/35 pb-4">PagarPal v1.0</p>
    </div>
  );
}

function HolidaysSection() {
  const { business } = useAuth();
  const queryClient = useQueryClient();
  const [open, setOpen] = React.useState(false);
  const [date, setDate] = React.useState("");
  const [name, setName] = React.useState("");
  const [isPaid, setIsPaid] = React.useState(true);
  const [type, setType] = React.useState<"custom" | "national" | "religious" | "regional">("custom");

  const { data: holidays } = useQuery({
    queryKey: ["holidays", business?.id],
    queryFn: () =>
      apiFetch<HolidayShape[]>(`/api/business/${business!.id}/holidays`),
    enabled: !!business?.id,
  });

  const addMutation = useMutation({
    mutationFn: () =>
      apiFetch<HolidayShape>(`/api/business/${business!.id}/holidays`, {
        method: "POST",
        body: JSON.stringify({ holidayDate: date, name, isPaid, holidayType: type }),
      }),
    onSuccess: () => {
      toast.success("Holiday added");
      queryClient.invalidateQueries({ queryKey: ["holidays", business?.id] });
      setOpen(false);
      setName("");
      setDate("");
      setIsPaid(true);
      setType("custom");
    },
    onError: (err) => toast.error(err instanceof Error ? err.message : "Failed"),
  });

  const deleteMutation = useMutation({
    mutationFn: (holidayDate: string) =>
      apiFetch(`/api/business/${business!.id}/holidays/${holidayDate}`, { method: "DELETE" }),
    onSuccess: () => {
      toast.success("Holiday removed");
      queryClient.invalidateQueries({ queryKey: ["holidays", business?.id] });
    },
    onError: (err) => toast.error(err instanceof Error ? err.message : "Failed"),
  });

  const upcoming = (holidays ?? [])
    .filter((h) => new Date(h.holidayDate) >= startOfDay(new Date(new Date().getFullYear(), 0, 1)))
    .sort((a, b) => new Date(a.holidayDate).getTime() - new Date(b.holidayDate).getTime());

  return (
    <Card className="bg-porcelain shadow-sm py-0 gap-0">
      <div className="px-5 pt-4 pb-2 flex items-center justify-between border-b border-border/40">
        <div className="flex items-center gap-2">
          <div className="size-8 rounded-lg bg-accent flex items-center justify-center">
            <CalendarPlus className="size-4 text-jungle-teal" />
          </div>
          <h2 className="text-sm font-semibold text-graphite">Holidays</h2>
        </div>
        <Dialog open={open} onOpenChange={setOpen}>
          <DialogTrigger asChild>
            <Button size="sm" variant="outline" className="h-8">
              <Plus className="size-4" /> Add
            </Button>
          </DialogTrigger>
          <DialogContent className="max-w-md">
            <DialogHeader>
              <DialogTitle>Add holiday</DialogTitle>
            </DialogHeader>
            <div className="space-y-4 py-2">
              <div className="space-y-1.5">
                <Label>Date</Label>
                <Input type="date" value={date} onChange={(e) => setDate(e.target.value)} />
              </div>
              <div className="space-y-1.5">
                <Label>Name</Label>
                <Input value={name} onChange={(e) => setName(e.target.value)} placeholder="e.g. Diwali" />
              </div>
              <div className="grid grid-cols-2 gap-3">
                <div className="space-y-1.5">
                  <Label>Type</Label>
                  <Select value={type} onValueChange={(v) => setType(v as typeof type)}>
                    <SelectTrigger><SelectValue /></SelectTrigger>
                    <SelectContent>
                      <SelectItem value="custom">Custom</SelectItem>
                      <SelectItem value="national">National</SelectItem>
                      <SelectItem value="religious">Religious</SelectItem>
                      <SelectItem value="regional">Regional</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div className="flex items-end gap-2 pb-1.5">
                  <Switch checked={isPaid} onCheckedChange={setIsPaid} id="paid" />
                  <Label htmlFor="paid" className="text-sm">Paid</Label>
                </div>
              </div>
            </div>
            <DialogFooter>
              <DialogClose asChild>
                <Button variant="outline">Cancel</Button>
              </DialogClose>
              <Button
                className="bg-jungle-teal hover:bg-jungle-teal/90 text-white"
                disabled={!date || !name || addMutation.isPending}
                onClick={() => addMutation.mutate()}
              >
                {addMutation.isPending ? "Adding…" : "Add holiday"}
              </Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      </div>
      <div className="p-3 max-h-80 overflow-y-auto scroll-area-thin">
        {upcoming.length === 0 ? (
          <p className="text-sm text-graphite/50 text-center py-6">
            No holidays added yet.
          </p>
        ) : (
          <div className="space-y-1.5">
            {upcoming.map((h) => (
              <div
                key={h.id}
                className="flex items-center gap-3 p-2.5 rounded-xl hover:bg-accent/30 group"
              >
                <div className="size-11 rounded-xl bg-accent flex flex-col items-center justify-center shrink-0">
                  <span className="text-[9px] font-medium text-graphite/50 uppercase">
                    {formatDate(h.holidayDate, { month: "short" })}
                  </span>
                  <span className="text-base font-bold text-jungle-teal leading-none">
                    {new Date(h.holidayDate).getDate()}
                  </span>
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-graphite truncate">{h.name}</p>
                  <p className="text-[11px] text-graphite/50">
                    {h.holidayType} · {h.isPaid ? "Paid" : "Unpaid"}
                  </p>
                </div>
                <button
                  onClick={() => deleteMutation.mutate(h.holidayDate)}
                  className="size-8 rounded-lg flex items-center justify-center text-graphite/30 hover:text-destructive hover:bg-destructive/10 opacity-0 group-hover:opacity-100 transition-opacity"
                >
                  <Trash2 className="size-4" />
                </button>
              </div>
            ))}
          </div>
        )}
      </div>
    </Card>
  );
}

function AppearanceSection() {
  const { theme, setTheme } = useTheme();
  const [mounted, setMounted] = React.useState(false);
  React.useEffect(() => setMounted(true), []);

  const isDark = mounted && theme === "dark";

  return (
    <Card className="bg-porcelain shadow-sm py-0 gap-0">
      <div className="px-4 pt-3.5 pb-3 flex items-center gap-2 border-b border-border/40">
        <div className="size-8 rounded-lg bg-accent flex items-center justify-center">
          <Palette className="size-4 text-jungle-teal" />
        </div>
        <h2 className="text-sm font-semibold text-graphite">Appearance</h2>
      </div>
      <div className="p-4 space-y-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2.5">
            <div className="size-9 rounded-xl bg-accent flex items-center justify-center">
              {isDark ? <Moon className="size-4 text-jungle-teal" /> : <Sun className="size-4 text-jungle-teal" />}
            </div>
            <div>
              <p className="text-sm font-medium text-graphite">Dark mode</p>
              <p className="text-[11px] text-graphite/55">Easier on the eyes at night</p>
            </div>
          </div>
          <Switch
            checked={isDark}
            onCheckedChange={(checked) => setTheme(checked ? "dark" : "light")}
            aria-label="Toggle dark mode"
          />
        </div>
      </div>
    </Card>
  );
}
