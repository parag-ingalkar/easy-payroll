"use client";

import type { PayrollRunShape } from "@/lib/types";
import { formatCurrency } from "@/lib/format";

/**
 * Generates and downloads a CSV file for a payroll run.
 */
export function exportPayrollCSV(run: PayrollRunShape, businessName: string) {
  const headers = [
    "Employee",
    "Present Days",
    "Half Days",
    "Paid Leave",
    "Unpaid Leave",
    "Holiday Days",
    "Overtime Hours",
    "Earned Salary",
    "Overtime Pay",
    "Additions",
    "Deductions",
    "Net Payable",
    "Status",
    "Paid Via",
    "Paid Date",
  ];

  const lineItems = run.lineItems ?? [];
  const rows = lineItems.map((item) => [
    item.employeeName,
    String(item.presentDays),
    String(item.halfDays),
    String(item.paidLeaveDays),
    String(item.unpaidLeaveDays),
    String(item.holidayDays),
    String(item.overtimeHours),
    String(item.earnedSalary),
    String(item.overtimePay),
    String(item.totalAdditions),
    String(item.totalDeductions),
    String(item.netPayable),
    item.status,
    item.paidVia ?? "",
    item.paidDate ? new Date(item.paidDate).toLocaleDateString("en-IN") : "",
  ]);

  const csv = [headers, ...rows]
    .map((row) => row.map(escapeCSV).join(","))
    .join("\n");

  const monthName = new Date(run.year, run.month - 1).toLocaleDateString("en-IN", { month: "short" });
  const filename = `payroll-${businessName.replace(/\s+/g, "-").toLowerCase()}-${monthName}-${run.year}.csv`;

  downloadCSV(csv, filename);
}

function escapeCSV(value: string): string {
  if (value.includes(",") || value.includes('"') || value.includes("\n")) {
    return `"${value.replace(/"/g, '""')}"`;
  }
  return value;
}

function downloadCSV(csv: string, filename: string) {
  const blob = new Blob([csv], { type: "text/csv;charset=utf-8;" });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  URL.revokeObjectURL(url);
}
