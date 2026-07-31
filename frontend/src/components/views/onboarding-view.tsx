"use client";

import * as React from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { toast } from "sonner";
import { Store, ArrowRight, Check } from "lucide-react";
import { useAuth } from "@/lib/auth-context";
import { apiFetch } from "@/lib/api";
import { Logo, Wordmark } from "@/components/brand";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { ToggleGroup, ToggleGroupItem } from "@/components/ui/toggle-group";
import { WEEKDAYS } from "@/lib/format";
import type { BusinessShape } from "@/lib/types";

const schema = z.object({
  name: z.string().min(2, "Business name is required"),
  divisorPolicy: z.enum(["26", "30", "calendar"]),
  defaultOvertimeMultiplier: z.number().min(1).max(5),
  defaultWorkingHours: z.number().int().min(1).max(24),
  defaultWeeklyOffDays: z.array(z.string()),
});

type FormValues = z.infer<typeof schema>;

const DIVISOR_OPTIONS = [
  {
    value: "30",
    label: "30 days (standard monthly)",
    desc: "baseRate / 30 × worked days",
  },
  {
    value: "26",
    label: "26 days (working days)",
    desc: "Excludes weekly offs",
  },
  {
    value: "calendar",
    label: "Calendar days",
    desc: "Uses actual days in month",
  },
];

export function OnboardingView() {
  const { refreshUser } = useAuth();
  const [submitting, setSubmitting] = React.useState(false);

  const {
    register,
    handleSubmit,
    setValue,
    watch,
    formState: { errors },
  } = useForm<FormValues>({
    resolver: zodResolver(schema),
    defaultValues: {
      name: "",
      divisorPolicy: "30",
      defaultOvertimeMultiplier: 1.5,
      defaultWorkingHours: 8,
      defaultWeeklyOffDays: ["sunday"],
    },
  });

  const offDays = watch("defaultWeeklyOffDays");
  const divisorPolicy = watch("divisorPolicy");

  const onSubmit = async (values: FormValues) => {
    setSubmitting(true);
    try {
      await apiFetch<BusinessShape>("/api/business", {
        method: "POST",
        body: JSON.stringify(values),
      });
      await refreshUser();
      toast.success("Business created! Welcome to PagarPal.");
    } catch (err) {
      toast.error(
        err instanceof Error ? err.message : "Could not create business",
      );
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="min-h-screen flex flex-col bg-background">
      <div className="flex-1 px-6 py-10 max-w-md mx-auto w-full">
        <div className="mb-8 flex flex-col items-center text-center pp-animate-in">
          <Logo size={56} />
          <Wordmark className="text-2xl mt-3" />
          <p className="text-sm text-graphite/60 mt-1">
            Set up your business to get started.
          </p>
        </div>

        <div className="bg-porcelain rounded-2xl border border-border/60 shadow-sm p-6 pp-animate-in">
          <div className="flex items-center gap-2 mb-6">
            <div className="size-9 rounded-xl bg-accent flex items-center justify-center">
              <Store className="size-4 text-jungle-teal" />
            </div>
            <h1 className="text-lg font-semibold text-graphite">
              Set up your business
            </h1>
          </div>

          <form onSubmit={handleSubmit(onSubmit)} className="space-y-5">
            <div className="space-y-1.5">
              <Label htmlFor="name">Business name *</Label>
              <Input
                id="name"
                placeholder="e.g. Sharma General Store"
                {...register("name")}
              />
              {errors.name && (
                <p className="text-xs text-destructive">
                  {errors.name.message}
                </p>
              )}
            </div>

            <div className="space-y-2">
              <Label>Salary divisor policy</Label>
              <div className="space-y-2">
                {DIVISOR_OPTIONS.map((opt) => (
                  <button
                    key={opt.value}
                    type="button"
                    onClick={() =>
                      setValue(
                        "divisorPolicy",
                        opt.value as "26" | "30" | "calendar",
                      )
                    }
                    className={`w-full text-left rounded-xl border p-3 transition-colors ${
                      divisorPolicy === opt.value
                        ? "border-jungle-teal bg-accent/50"
                        : "border-border bg-porcelain hover:bg-accent/30"
                    }`}
                  >
                    <div className="flex items-center justify-between">
                      <span className="text-sm font-medium text-graphite">
                        {opt.label}
                      </span>
                      {divisorPolicy === opt.value && (
                        <Check className="size-4 text-jungle-teal" />
                      )}
                    </div>
                    <span className="text-xs text-graphite/55">{opt.desc}</span>
                  </button>
                ))}
              </div>
            </div>

            <div className="grid grid-cols-2 gap-3">
              <div className="space-y-1.5">
                <Label htmlFor="defaultOvertimeMultiplier">
                  Overtime rate (×)
                </Label>
                <Input
                  id="defaultOvertimeMultiplier"
                  type="number"
                  step="0.1"
                  {...register("defaultOvertimeMultiplier", {
                    valueAsNumber: true,
                  })}
                />
              </div>
              <div className="space-y-1.5">
                <Label htmlFor="defaultWorkingHours">Working hrs/day</Label>
                <Input
                  id="defaultWorkingHours"
                  type="number"
                  {...register("defaultWorkingHours", { valueAsNumber: true })}
                />
              </div>
            </div>

            <div className="space-y-2">
              <Label>Weekly off days (default)</Label>
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

            <Button
              type="submit"
              className="w-full bg-jungle-teal hover:bg-jungle-teal/90 text-white h-11"
              disabled={submitting}
            >
              {submitting ? "Creating…" : "Create business"}
              {!submitting && <ArrowRight className="size-4" />}
            </Button>
          </form>
        </div>
      </div>
    </div>
  );
}
