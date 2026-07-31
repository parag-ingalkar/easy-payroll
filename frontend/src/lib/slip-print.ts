"use client";

import type { PayrollLineItemShape, BusinessShape } from "@/lib/types";
import { formatCurrency, formatDate, MONTH_NAMES } from "@/lib/format";

type SlipData = {
  business: Pick<BusinessShape, "name">;
  employee: { name: string; phone: string; designation: string | null; salaryType: string };
  item: PayrollLineItemShape;
  year: number;
  month: number;
};

/**
 * Opens a print-friendly salary slip in a new window.
 * The user can then use the browser's "Save as PDF" from the print dialog.
 */
export function openSalarySlipPrint(data: SlipData) {
  const { business, employee, item, year, month } = data;
  const monthLabel = `${MONTH_NAMES[month - 1]} ${year}`;
  const slipId = `PP-${year}${String(month).padStart(2, "0")}-${item.employeeId.slice(-6).toUpperCase()}`;
  const isPaid = item.status === "paid";

  const html = `<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>Salary Slip — ${employee.name} — ${monthLabel}</title>
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
    color: #333;
    background: #f5f5f5;
    padding: 24px;
    -webkit-print-color-adjust: exact;
    print-color-adjust: exact;
  }
  .slip {
    max-width: 640px;
    margin: 0 auto;
    background: #fff;
    border-radius: 16px;
    overflow: hidden;
    box-shadow: 0 4px 24px rgba(0,0,0,0.08);
  }
  .header {
    background: linear-gradient(135deg, #668f80 0%, #5b7a6c 100%);
    color: #fff;
    padding: 24px 28px;
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
  }
  .brand { display: flex; align-items: center; gap: 10px; }
  .brand-mark {
    width: 36px; height: 36px;
    background: rgba(255,255,255,0.2);
    border-radius: 10px;
    display: flex; align-items: center; justify-content: center;
    font-weight: 700; font-size: 16px;
  }
  .brand-name { font-size: 18px; font-weight: 700; letter-spacing: -0.3px; }
  .brand-tag { font-size: 11px; opacity: 0.8; }
  .slip-id { text-align: right; font-size: 11px; opacity: 0.85; }
  .slip-id strong { display: block; font-size: 13px; opacity: 1; }

  .title { padding: 20px 28px 12px; border-bottom: 1px solid #eee; }
  .title h1 { font-size: 18px; font-weight: 700; color: #333; }
  .title .period { font-size: 12px; color: #777; margin-top: 2px; }

  .parties { padding: 16px 28px; display: flex; justify-content: space-between; gap: 16px; }
  .party { flex: 1; }
  .party-label { font-size: 10px; text-transform: uppercase; letter-spacing: 0.5px; color: #999; margin-bottom: 4px; }
  .party-name { font-size: 14px; font-weight: 600; color: #333; }
  .party-meta { font-size: 11px; color: #666; margin-top: 2px; line-height: 1.5; }

  .summary {
    margin: 0 28px 20px;
    background: #fbfefb;
    border: 1px solid #e8e0d4;
    border-radius: 12px;
    overflow: hidden;
  }
  .summary-row {
    display: flex; justify-content: space-between; align-items: center;
    padding: 10px 16px;
    border-bottom: 1px solid #f0ebe2;
    font-size: 13px;
  }
  .summary-row:last-child { border-bottom: 0; }
  .summary-row .label { color: #555; }
  .summary-row .value { font-weight: 600; color: #333; }
  .summary-row.positive .value { color: #047857; }
  .summary-row.negative .value { color: #b91c1c; }
  .summary-row.total {
    background: #f4f0e8;
    font-size: 15px;
    padding: 14px 16px;
  }
  .summary-row.total .label { font-weight: 700; color: #333; }
  .summary-row.total .value { font-weight: 800; color: #668f80; font-size: 17px; }

  .attendance {
    margin: 0 28px 20px;
    display: grid; grid-template-columns: repeat(3, 1fr); gap: 8px;
  }
  .att-box {
    background: #f7f3ec;
    border-radius: 10px;
    padding: 10px;
    text-align: center;
  }
  .att-box .n { font-size: 18px; font-weight: 700; color: #333; line-height: 1; }
  .att-box .l { font-size: 10px; color: #888; margin-top: 3px; }

  .footer {
    padding: 16px 28px 24px;
    border-top: 1px solid #eee;
    display: flex; justify-content: space-between; align-items: flex-end;
  }
  .status {
    display: inline-flex; align-items: center; gap: 6px;
    padding: 6px 12px; border-radius: 999px;
    font-size: 11px; font-weight: 600;
    background: ${isPaid ? "#d1fae5" : "#fef3c7"};
    color: ${isPaid ? "#047857" : "#92400e"};
  }
  .status .dot { width: 6px; height: 6px; border-radius: 50%; background: currentColor; }
  .sign { text-align: right; }
  .sign-line { width: 140px; border-top: 1px solid #999; margin-bottom: 4px; margin-left: auto; }
  .sign-label { font-size: 11px; color: #666; }

  .note {
    padding: 0 28px 20px;
    font-size: 10px; color: #999; line-height: 1.5;
  }

  @media print {
    body { background: #fff; padding: 0; }
    .slip { box-shadow: none; max-width: 100%; }
    @page { margin: 12mm; }
  }
</style>
</head>
<body>
  <div class="slip">
    <div class="header">
      <div class="brand">
        <div class="brand-mark">P</div>
        <div>
          <div class="brand-name">${escapeHtml(business.name)}</div>
          <div class="brand-tag">Salary Slip · PagarPal</div>
        </div>
      </div>
      <div class="slip-id">
        Slip ID<br/><strong>${slipId}</strong>
      </div>
    </div>

    <div class="title">
      <h1>Salary Slip</h1>
      <div class="period">Pay period: ${monthLabel}</div>
    </div>

    <div class="parties">
      <div class="party">
        <div class="party-label">Employer</div>
        <div class="party-name">${escapeHtml(business.name)}</div>
      </div>
      <div class="party" style="text-align:right">
        <div class="party-label">Employee</div>
        <div class="party-name">${escapeHtml(employee.name)}</div>
        <div class="party-meta">
          ${employee.designation ? escapeHtml(employee.designation) + "<br/>" : ""}
          ${escapeHtml(employee.phone)}
        </div>
      </div>
    </div>

    <div class="summary">
      <div class="summary-row">
        <span class="label">Earned salary</span>
        <span class="value">${formatCurrency(item.earnedSalary)}</span>
      </div>
      ${item.overtimePay > 0 ? `
      <div class="summary-row positive">
        <span class="label">Overtime pay (${item.overtimeHours}h)</span>
        <span class="value">+ ${formatCurrency(item.overtimePay)}</span>
      </div>` : ""}
      ${item.totalAdditions > 0 ? `
      <div class="summary-row positive">
        <span class="label">Additions</span>
        <span class="value">+ ${formatCurrency(item.totalAdditions)}</span>
      </div>` : ""}
      ${item.totalDeductions > 0 ? `
      <div class="summary-row negative">
        <span class="label">Deductions</span>
        <span class="value">- ${formatCurrency(item.totalDeductions)}</span>
      </div>` : ""}
      <div class="summary-row total">
        <span class="label">Net payable</span>
        <span class="value">${formatCurrency(item.netPayable)}</span>
      </div>
    </div>

    <div class="attendance">
      <div class="att-box"><div class="n">${item.presentDays}</div><div class="l">Present</div></div>
      <div class="att-box"><div class="n">${item.halfDays}</div><div class="l">Half days</div></div>
      <div class="att-box"><div class="n">${item.paidLeaveDays}</div><div class="l">Paid leave</div></div>
      <div class="att-box"><div class="n">${item.unpaidLeaveDays}</div><div class="l">Unpaid leave</div></div>
      <div class="att-box"><div class="n">${item.holidayDays}</div><div class="l">Holidays</div></div>
      <div class="att-box"><div class="n">${item.overtimeHours}h</div><div class="l">Overtime</div></div>
    </div>

    <div class="footer">
      <div>
        <div class="status">
          <span class="dot"></span>
          ${isPaid ? `Paid via ${item.paidVia || "cash"}${item.paidDate ? ` on ${formatDate(item.paidDate)}` : ""}` : "Payment pending"}
        </div>
      </div>
      <div class="sign">
        <div class="sign-line"></div>
        <div class="sign-label">Authorised signature</div>
      </div>
    </div>

    <div class="note">
      This is a computer-generated salary slip from PagarPal. Generated on ${formatDate(new Date(), { day: "2-digit", month: "long", year: "numeric" })}.
    </div>
  </div>

  <script>
    window.onload = function() { setTimeout(function() { window.print(); }, 300); };
  </script>
</body>
</html>`;

  const w = window.open("", "_blank", "width=720,height=900");
  if (!w) {
    alert("Please allow popups to download the salary slip.");
    return;
  }
  w.document.open();
  w.document.write(html);
  w.document.close();
}

function escapeHtml(s: string): string {
  return s
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#39;");
}
