import type { AttendanceStatus, SalaryType, TransactionType } from "./types";

export function formatCurrency(amount: number, currency = "₹"): string {
  const sign = amount < 0 ? "-" : "";
  const abs = Math.abs(amount);
  const formatted = abs.toLocaleString("en-IN", {
    minimumFractionDigits: 0,
    maximumFractionDigits: 2,
  });
  return `${sign}${currency}${formatted}`;
}

/**
 * Compact currency for tight spaces — ₹23.8k, ₹1.2L, ₹1.4Cr.
 * Never truncates with ellipsis; always fits.
 */
export function formatCurrencyCompact(amount: number, currency = "₹"): string {
  const sign = amount < 0 ? "-" : "";
  const abs = Math.abs(amount);
  let body: string;
  if (abs >= 1_00_00_000) body = `${(abs / 1_00_00_000).toFixed(1)}Cr`;
  else if (abs >= 1_00_000) body = `${(abs / 1_00_000).toFixed(1)}L`;
  else if (abs >= 1_000) body = `${(abs / 1_000).toFixed(1)}k`;
  else body = `${abs}`;
  return `${sign}${currency}${body}`;
}

export function formatDate(date: string | Date, opts?: Intl.DateTimeFormatOptions): string {
  const d = typeof date === "string" ? new Date(date) : date;
  return d.toLocaleDateString("en-IN", opts ?? { day: "2-digit", month: "short", year: "numeric" });
}

export function formatTime(date: string | Date): string {
  const d = typeof date === "string" ? new Date(date) : date;
  return d.toLocaleTimeString("en-IN", { hour: "2-digit", minute: "2-digit" });
}

export const MONTH_NAMES = [
  "January", "February", "March", "April", "May", "June",
  "July", "August", "September", "October", "November", "December",
];

export const MONTH_SHORT = [
  "Jan", "Feb", "Mar", "Apr", "May", "Jun",
  "Jul", "Aug", "Sep", "Oct", "Nov", "Dec",
];

export const WEEKDAYS = ["sunday", "monday", "tuesday", "wednesday", "thursday", "friday", "saturday"];
export const WEEKDAY_SHORT = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"];

export function ymd(date: Date): string {
  const y = date.getFullYear();
  const m = String(date.getMonth() + 1).padStart(2, "0");
  const d = String(date.getDate()).padStart(2, "0");
  return `${y}-${m}-${d}`;
}

/**
 * Parse a "YYYY-MM-DD" string as UTC midnight.
 * This avoids timezone-shift bugs where `new Date("2026-07-25")`
 * combined with server-local `setHours()` can move the date to the
 * previous day.
 */
export function ymdToUTCDate(s: string): Date {
  return new Date(s + "T00:00:00.000Z");
}

export function parseYmd(s: string): Date {
  const [y, m, d] = s.split("-").map(Number);
  return new Date(y, m - 1, d);
}

export function startOfDay(date: Date): Date {
  const d = new Date(date);
  d.setHours(0, 0, 0, 0);
  return d;
}

export function addDays(date: Date, days: number): Date {
  const d = new Date(date);
  d.setDate(d.getDate() + days);
  return d;
}

export function daysInMonth(year: number, month: number): number {
  return new Date(year, month, 0).getDate();
}

export const ATTENDANCE_META: Record<
  AttendanceStatus,
  { label: string; short: string; color: string; bg: string; ring: string }
> = {
  present: {
    label: "Present",
    short: "P",
    color: "text-emerald-700",
    bg: "bg-emerald-100",
    ring: "ring-emerald-400",
  },
  half_day: {
    label: "Half Day",
    short: "H",
    color: "text-amber-700",
    bg: "bg-amber-100",
    ring: "ring-amber-400",
  },
  paid_leave: {
    label: "Paid Leave",
    short: "PL",
    color: "text-sky-700",
    bg: "bg-sky-100",
    ring: "ring-sky-400",
  },
  unpaid_leave: {
    label: "Unpaid Leave",
    short: "UL",
    color: "text-rose-700",
    bg: "bg-rose-100",
    ring: "ring-rose-400",
  },
};

export const TRANSACTION_META: Record<
  TransactionType,
  { label: string; color: string; bg: string; sign: string }
> = {
  addition: { label: "Addition", color: "text-emerald-700", bg: "bg-emerald-100", sign: "+" },
  deduction: { label: "Deduction", color: "text-rose-700", bg: "bg-rose-100", sign: "-" },
};

export const SALARY_TYPE_LABELS: Record<SalaryType, string> = {
  monthly: "Monthly Salary",
  daily: "Daily Wage",
  hourly: "Hourly Wage",
};

export function parseJsonArray(s: string | null | undefined): string[] {
  if (!s) return [];
  try {
    const v = JSON.parse(s);
    return Array.isArray(v) ? v.map(String) : [];
  } catch {
    return [];
  }
}

export function generateToken(): string {
  return (
    Math.random().toString(36).slice(2) +
    Math.random().toString(36).slice(2) +
    Math.random().toString(36).slice(2)
  ).slice(0, 32);
}
