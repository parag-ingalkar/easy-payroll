"use client";

import * as React from "react";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";
import { CheckCheck, CalendarOff, ChevronLeft, ChevronRight } from "lucide-react";

import { apiFetch } from "@/lib/api";
import { useAuth } from "@/lib/auth-context";
import {
  WEEKDAYS,
  ymd,
  startOfDay,
  addDays,
  ATTENDANCE_META,
} from "@/lib/format";
import type {
  AttendanceShape,
  AttendanceStatus,
  EmployeeShape,
  HolidayShape,
} from "@/lib/types";

import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Calendar } from "@/components/ui/calendar";
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from "@/components/ui/popover";
import { cn } from "@/lib/utils";

type AttendanceRecord = AttendanceShape;

function toOvertimeNumber(value: unknown): number {
  const numberValue =
    typeof value === "number" ? value : Number.parseFloat(String(value));

  return Number.isFinite(numberValue) && numberValue >= 0 ? numberValue : 0;
}

export function AttendanceView() {
  const { business } = useAuth();
  const queryClient = useQueryClient();

  const [selectedDate, setSelectedDate] = React.useState(() =>
    startOfDay(new Date()),
  );
  const [calendarOpen, setCalendarOpen] = React.useState(false);

  const selectedStr = ymd(selectedDate);
  const todayStr = ymd(startOfDay(new Date()));
  const isToday = selectedStr === todayStr;
  const isFuture = selectedDate > startOfDay(new Date());

  const { data: employees } = useQuery({
    queryKey: ["employees", business?.id],
    queryFn: () =>
      apiFetch<EmployeeShape[]>(
        `/api/business/${business!.id}/employees?include_inactive=true`,
      ),
    enabled: Boolean(business?.id),
  });

  const { data: records = [], isLoading } = useQuery({
    queryKey: ["attendance", business?.id, selectedStr],
    queryFn: () =>
      apiFetch<AttendanceRecord[]>(
        `/api/business/${business!.id}/attendances/by-date/${selectedStr}`,
      ),
    enabled: Boolean(business?.id),
  });

  const { data: holidays = [] } = useQuery({
    queryKey: ["holidays", business?.id],
    queryFn: () =>
      apiFetch<HolidayShape[]>(`/api/business/${business!.id}/holidays`),
    enabled: Boolean(business?.id),
  });

  const activeEmployees = employees?.filter((employee) => employee.isActive) ?? [];

  const recordMap = React.useMemo(() => {
    return new Map(records.map((record) => [record.employeeId, record]));
  }, [records]);

  const holidayMap = React.useMemo(() => {
    const map = new Map<string, HolidayShape>();

    for (const holiday of holidays) {
      const date = new Date(holiday.holidayDate);
      const key = `${date.getUTCFullYear()}-${String(
        date.getUTCMonth() + 1,
      ).padStart(2, "0")}-${String(date.getUTCDate()).padStart(2, "0")}`;

      map.set(key, holiday);
    }

    return map;
  }, [holidays]);

  const selectedHoliday = holidayMap.get(selectedStr);
  const isHoliday = Boolean(selectedHoliday);

  const isEmployeeBlocked = React.useCallback(
    (employee: EmployeeShape) => {
      const offDays = Array.isArray(employee.weeklyOffDays)
        ? employee.weeklyOffDays
        : [];

      return isHoliday || offDays.includes(WEEKDAYS[selectedDate.getDay()]);
    },
    [isHoliday, selectedDate],
  );

  const eligibleEmployees = activeEmployees.filter(
    (employee) => !isEmployeeBlocked(employee),
  );

  const markedCount = eligibleEmployees.filter((employee) =>
    recordMap.has(employee.id),
  ).length;

  const upsert = React.useCallback(
    async (
      employeeId: string,
      status: AttendanceStatus,
      overtimeHours: number,
    ) => {
      if (!business?.id) return;

      // This is the only overtime value used in UI/cache/request.
      const safeOvertimeHours = toOvertimeNumber(overtimeHours);

      const queryKey = ["attendance", business.id, selectedStr];
      const previousRecords =
        queryClient.getQueryData<AttendanceRecord[]>(queryKey) ?? [];

      const existing = previousRecords.find(
        (record) => record.employeeId === employeeId,
      );

      const updated: AttendanceRecord = {
        id: existing?.id ?? `temp-${employeeId}`,
        employeeId,
        date: selectedStr,
        status,
        overtimeHours: safeOvertimeHours,
        createdAt: existing?.createdAt ?? "",
        updatedAt: existing?.updatedAt ?? "",
      };

      const nextRecords = existing
        ? previousRecords.map((record) =>
            record.employeeId === employeeId ? updated : record,
          )
        : [...previousRecords, updated];

      queryClient.setQueryData(queryKey, nextRecords);

      try {
        await apiFetch(
          `/api/business/${business.id}/employees/${employeeId}/attendances/${selectedStr}`,
          {
            method: "PUT",
            body: JSON.stringify({
              status,
              overtimeHours: safeOvertimeHours,
            }),
          },
        );

        queryClient.invalidateQueries({ queryKey: ["dashboard"] });
        queryClient.invalidateQueries({ queryKey });
      } catch (error) {
        queryClient.setQueryData(queryKey, previousRecords);
        toast.error(
          error instanceof Error ? error.message : "Failed to save attendance",
        );
      }
    },
    [business?.id, queryClient, selectedStr],
  );

  const markAllPresent = React.useCallback(async () => {
    if (!business?.id) return;

    const unmarked = eligibleEmployees.filter(
      (employee) => !recordMap.has(employee.id),
    );

    if (unmarked.length === 0) {
      toast.info("All eligible employees are already marked");
      return;
    }

    const queryKey = ["attendance", business.id, selectedStr];
    const previousRecords =
      queryClient.getQueryData<AttendanceRecord[]>(queryKey) ?? [];

    const optimisticRecords = [
      ...previousRecords,
      ...unmarked.map(
        (employee): AttendanceRecord => ({
          id: `temp-${employee.id}`,
          employeeId: employee.id,
          date: selectedStr,
          status: "present",
          overtimeHours: 0,
          createdAt: "",
          updatedAt: "",
        }),
      ),
    ];

    queryClient.setQueryData(queryKey, optimisticRecords);

    try {
      await apiFetch(
        `/api/business/${business.id}/attendances/bulk?attendance_date=${selectedStr}`,
        {
          method: "PUT",
          body: JSON.stringify({
            entries: unmarked.map((employee) => ({
              employeeId: employee.id,
              status: "present",
              overtimeHours: 0,
            })),
          }),
        },
      );

      toast.success(`Marked ${unmarked.length} employee(s) present`);
      queryClient.invalidateQueries({ queryKey: ["dashboard"] });
      queryClient.invalidateQueries({ queryKey });
    } catch {
      queryClient.setQueryData(queryKey, previousRecords);
      toast.error("Failed to mark all employees present");
    }
  }, [
    business?.id,
    eligibleEmployees,
    queryClient,
    recordMap,
    selectedStr,
  ]);

  return (
    <div className="space-y-4 pp-animate-in">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold text-graphite">Attendance</h1>
          <p className="text-xs text-graphite/60">
            {markedCount}/{eligibleEmployees.length} marked
          </p>
        </div>

        {eligibleEmployees.length > markedCount && (
          <Button
            variant="outline"
            size="sm"
            onClick={markAllPresent}
            className="h-8 border-jungle-teal/30 text-jungle-teal"
          >
            <CheckCheck className="size-3.5" />
            All present
          </Button>
        )}
      </div>

      <div className="flex items-center justify-between rounded-xl border border-border/60 bg-porcelain px-2 py-1.5">
        <button
          type="button"
          onClick={() => setSelectedDate((date) => addDays(date, -1))}
          className="size-9 rounded-lg text-graphite/70 hover:bg-accent/60"
          aria-label="Previous day"
        >
          <ChevronLeft className="mx-auto size-5" />
        </button>

        <Popover open={calendarOpen} onOpenChange={setCalendarOpen}>
          <PopoverTrigger asChild>
            <button
              type="button"
              className="flex flex-1 flex-col items-center rounded-lg py-1 hover:bg-accent/40"
            >
              <span className="text-[13px] font-semibold text-graphite">
                {selectedDate.toLocaleDateString("en-IN", {
                  weekday: "long",
                })}
              </span>
              <span className="text-[11px] text-graphite/60">
                {selectedDate.toLocaleDateString("en-IN", {
                  day: "numeric",
                  month: "long",
                  year: "numeric",
                })}
                {isToday && " · Today"}
              </span>
            </button>
          </PopoverTrigger>

          <PopoverContent className="w-auto p-0" align="center">
            <Calendar
              mode="single"
              selected={selectedDate}
              onSelect={(date) => {
                if (!date) return;
                setSelectedDate(startOfDay(date));
                setCalendarOpen(false);
              }}
              disabled={(date) => date > startOfDay(new Date())}
              initialFocus
            />
          </PopoverContent>
        </Popover>

        <button
          type="button"
          onClick={() => setSelectedDate((date) => addDays(date, 1))}
          disabled={isToday || isFuture}
          className="size-9 rounded-lg text-graphite/70 hover:bg-accent/60 disabled:cursor-not-allowed disabled:opacity-30"
          aria-label="Next day"
        >
          <ChevronRight className="mx-auto size-5" />
        </button>
      </div>

      {isHoliday && (
        <Card className="border-violet-200 bg-violet-50 p-4">
          <div className="flex items-center gap-3">
            <CalendarOff className="size-5 text-violet-600" />
            <div>
              <p className="text-sm font-medium text-violet-900">
                {selectedHoliday?.name}
              </p>
              <p className="text-xs text-violet-700">
                Attendance marking is disabled for this holiday.
              </p>
            </div>
          </div>
        </Card>
      )}

      {isLoading ? (
        <div className="space-y-3">
          {[0, 1, 2].map((item) => (
            <div
              key={item}
              className="h-24 animate-pulse rounded-2xl bg-graphite/10"
            />
          ))}
        </div>
      ) : (
        <div className="space-y-2.5">
          {activeEmployees.map((employee) => {
            const record = recordMap.get(employee.id);
            const status = record?.status ?? null;

            // Crucial: conversion occurs before rendering or calculating.
            const overtimeHours = toOvertimeNumber(record?.overtimeHours);

            const offDays = Array.isArray(employee.weeklyOffDays)
              ? employee.weeklyOffDays
              : [];

            const weekdayName = WEEKDAYS[selectedDate.getDay()];
            const isWeeklyOff = offDays.includes(weekdayName);
            const blocked = isHoliday || isWeeklyOff;

            return (
              <Card
                key={employee.id}
                className={cn(
                  "bg-porcelain p-3.5 shadow-sm",
                  blocked && "opacity-60",
                )}
              >
                <div className="mb-2.5 flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-graphite">
                      {employee.name}
                    </p>
                    <p className="text-[11px] text-graphite/55">
                      {employee.designation || employee.salaryType}
                    </p>
                  </div>

                  {blocked ? (
                    <span className="text-xs text-graphite/55">
                      {isHoliday
                        ? "Holiday"
                        : `Weekly off (${weekdayName})`}
                    </span>
                  ) : status ? (
                    <span
                      className={cn(
                        "rounded-full px-2 py-0.5 text-[10px] font-medium",
                        ATTENDANCE_META[status].bg,
                        ATTENDANCE_META[status].color,
                      )}
                    >
                      {ATTENDANCE_META[status].short}
                    </span>
                  ) : null}
                </div>

                {!blocked && (
                  <>
                    <div className="mb-2 grid grid-cols-4 gap-1.5">
                      {(Object.keys(ATTENDANCE_META) as AttendanceStatus[]).map(
                        (newStatus) => {
                          const meta = ATTENDANCE_META[newStatus];

                          return (
                            <button
                              key={newStatus}
                              type="button"
                              onClick={() =>
                                upsert(employee.id, newStatus, overtimeHours)
                              }
                              className={cn(
                                "rounded-lg border py-1.5 text-xs font-medium",
                                status === newStatus
                                  ? cn(
                                      meta.bg,
                                      meta.color,
                                      "border-transparent ring-2",
                                      meta.ring,
                                    )
                                  : "border-border/60 bg-porcelain text-graphite/50 hover:bg-accent/40",
                              )}
                            >
                              {meta.short}
                            </button>
                          );
                        },
                      )}
                    </div>

                    {(status === "present" || status === "half_day") && (
                      <div className="flex items-center justify-between rounded-lg bg-muted px-3 py-2">
                        <span className="text-xs text-graphite/60">
                          Overtime hours
                        </span>

                        <input
                          type="number"
                          min="0"
                          step="0.5"
                          value={overtimeHours}
                          onChange={(event) => {
                            const nextValue = toOvertimeNumber(
                              event.target.value,
                            );

                            upsert(employee.id, status, nextValue);
                          }}
                          className="w-20 rounded-md border border-border/60 bg-porcelain px-2 py-1 text-right text-sm font-semibold text-graphite"
                          aria-label={`Overtime hours for ${employee.name}`}
                        />
                      </div>
                    )}
                  </>
                )}
              </Card>
            );
          })}
        </div>
      )}
    </div>
  );
}