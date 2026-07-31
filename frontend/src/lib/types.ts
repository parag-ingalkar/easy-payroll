// ---------------------------------------------------------------------------
// Enums / unions
// ---------------------------------------------------------------------------

export type Role = "OWNER" | "EMPLOYEE";

export type SalaryType = "monthly" | "daily" | "hourly";

export type AttendanceStatus =
  | "present"
  | "paid_leave"
  | "unpaid_leave"
  | "half_day";

export type TransactionType = "addition" | "deduction";

export type DivisorPolicy = "26" | "30" | "calendar";

export type PaymentMethod = "cash" | "upi" | "bank";

export type HolidayType = "custom" | "national" | "religious" | "regional";

// ---------------------------------------------------------------------------
// Auth
// ---------------------------------------------------------------------------

export type SessionShape = {
  id: string;
  email: string;
  name: string;
  roles: string[];
};

// ---------------------------------------------------------------------------
// Business
// ---------------------------------------------------------------------------

export type BusinessShape = {
  id: string;
  ownerId: string;
  name: string;
  slug: string;
  divisorPolicy: string;
  defaultOvertimeMultiplier: number;
  defaultWeeklyOffDays: string[];
  defaultWorkingHours: number;
  createdAt: string;
};

// ---------------------------------------------------------------------------
// Employee
// ---------------------------------------------------------------------------

export type EmployeeShape = {
  id: string;
  businessId: string;
  name: string;
  phone: string | null;
  designation: string | null;
  salaryType: string;
  baseRate: number;
  overtimeMultiplier: number;
  weeklyOffDays: string[];
  workingHours: number;
  joiningDate: string | null;
  isActive: boolean;
  createdAt: string;
};

// ---------------------------------------------------------------------------
// Attendance
// ---------------------------------------------------------------------------

export type AttendanceShape = {
  id: string;
  employeeId: string;
  date: string;
  status: string;
  overtimeHours: number;
  createdAt: string;
  updatedAt: string;
};

// ---------------------------------------------------------------------------
// Transaction
// ---------------------------------------------------------------------------

export type TransactionShape = {
  id: string;
  employeeId: string;
  transactionDate: string;
  type: string;
  amount: number;
  description: string;
  createdAt: string;
};

// ---------------------------------------------------------------------------
// Holiday
// ---------------------------------------------------------------------------

export type HolidayShape = {
  id: string;
  businessId: string;
  holidayDate: string;
  name: string;
  holidayType: string;
  isPaid: boolean;
};

// ---------------------------------------------------------------------------
// Payroll
// ---------------------------------------------------------------------------

export type PayrollWarningShape = {
  id: string;
  payrollLineItemId: string;
  warningType: string;
  affectedDates: string[];
  message: string;
  createdAt: string;
};

export type PayrollLineItemShape = {
  id: string;
  payrollRunId: string;
  businessId: string;
  employeeId: string;
  employeeName: string;
  salaryType: string;
  baseRate: number;
  divisorPolicyUsed: string | null;
  overtimeMultiplierUsed: number;
  workingHoursUsed: number;
  presentDays: number;
  halfDays: number;
  paidLeaveDays: number;
  unpaidLeaveDays: number;
  holidayDays: number;
  weeklyOffDaysCount: number;
  overtimeHours: number;
  earnedSalary: number;
  overtimePay: number;
  totalAdditions: number;
  totalDeductions: number;
  netPayable: number;
  status: string;
  paidVia: string | null;
  paidDate: string | null;
};

export type PayrollRunShape = {
  id: string;
  businessId: string;
  month: number;
  year: number;
  status: string;
  totalAmountDue: number;
  isWarning: boolean;
  createdAt: string;
  updatedAt: string;
  lineItems?: PayrollLineItemShape[];
  warnings?: PayrollWarningShape[];
  isPaid: boolean;
};

// ---------------------------------------------------------------------------
// Dashboard
// ---------------------------------------------------------------------------

export type TrendDayShape = {
  day: string;
  date: string;
  present: number;
  half: number;
  leave: number;
  absent: number;
};

export type PayrollMonthShape = {
  month: string;
  label: string;
  total: number;
  paid: number;
};

export type PayrollInfoShape = {
  status: string;
  totalPayable: number;
  paidCount: number;
  totalCount: number;
};

export type DashboardShape = {
  business: Record<string, string>;
  activeEmployees: number;
  pendingAttendance: number;
  presentToday: number;
  halfToday: number;
  onLeaveToday: number;
  payroll: PayrollInfoShape;
  monthlyAdditions: number;
  monthlyDeductions: number;
  month: number;
  monthName: string;
  year: number;
  trend: TrendDayShape[];
  payrollHistory: PayrollMonthShape[];
  projectedMonthlyCost: number;
  ytdPaid: number;
};
