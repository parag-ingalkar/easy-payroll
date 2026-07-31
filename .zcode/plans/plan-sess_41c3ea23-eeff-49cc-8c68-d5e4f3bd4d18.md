# Plan: Attendance & Payroll Features

## Context & confirmed decisions
- **Architecture**: hexagonal/vertical-slice under `backend/app/features/<feature>/{domain,application,infrastructure,presentation}`. Each feature = 12 files. New features mirror `transaction` (deepest existing template).
- **Transaction summary buckets** → `total_additions` / `total_deductions` (matches existing `TransactionType {ADDITION, DEDUCTION }`). No data-model change to transactions.
- **Tests** → add pytest infra + pure-Python unit tests for the payroll *engine* only (no DB/integration tests).
- **Shared enums rule** (your note): payroll will **import** `WeekDay` from `app.shared.enums`, `SalaryType` from employee domain, `AttendanceStatus` from attendance domain, `DivisorPolicy` from business domain — never redefine them. (`AttendanceStatus` is legitimately attendance-owned, just as `SalaryType` is employee-owned.)
- **divisor_policy lives on `Business`** (not Employee) in our model — so all line items in one run share the business's divisor; it's snapshotted per-row as `divisor_policy_used` for display.

The reference `services.py` you pasted is the engine template; I'll adapt its imports/enum names to our real paths and change its 3-bucket transaction sum into additions/deductions.

---

## Milestone 0 — Cross-cutting prep
Small enabling changes before the two features.

**0a. Extend the transaction feature with a date-range read** (payroll needs it)
- `transaction/infrastructure/repositories.py`: add `get_by_employee_and_date_range(employee_id, start_date, end_date) -> list[Transaction]` (reuse the existing `select(...)` style, filter `transaction_date` between).
- `transaction/application/ports.py` `TransactionRepositoryPort`: add the method signature.
- `transaction/application/services.py` `TransactionService`: add `get_by_employee_and_date_range(...)` passthrough.
- This is additive — no change to existing transaction endpoints.

**0b. Test infrastructure** (dev-only)
- `backend/pyproject.toml`: add dev deps `pytest`, `pytest-asyncio`, `httpx`; a `[tool.pytest.ini_options]` block (`asyncio_mode = "auto"`, `testpaths = ["tests"]`).
- `backend/tests/conftest.py`: minimal fixtures (no DB needed for engine tests).
- `backend/tests/features/payroll/domain/test_services.py`: unit tests for the engine (see Milestone 2).

**0c. Alembic env** — each new model gets a `# noqa: F401` import line in `backend/alembic/env.py` (done per-feature below).

---

## Milestone 1 — Attendance feature
API contract: `employees/<employee_id>/attendances/<date>`, PUT (full-record upsert), one record per (employee, date).

### 1a. Domain
- `attendance/domain/value_objects.py` → `AttendanceStatus(StrEnum)`: `PRESENT="present"`, `PAID_LEAVE="paid_leave"`, `UNPAID_LEAVE="unpaid_leave"`, `HALF_DAY="half_day"`. (ADR-006 StrEnum.)
- `attendance/domain/entities.py` → `AttendanceRecord` dataclass:
  - fields: `id, employee_id, date, status: AttendanceStatus, overtime_hours: Decimal, created_at, updated_at`.
  - methods: `create(...)` (validates `overtime_hours >= 0`), `update(*, status, overtime_hours)` (PATCH, re-validates ot), `ensure_belongs_to_employee(employee_id)`.
- `attendance/domain/exceptions.py` → `AttendanceNotFoundError(NotFoundError)`, `AttendanceNotOwnedError(ForbiddenError)`, `InvalidOvertimeHoursError(ValidationError)` — subclass `app.core.exception_handler` bases, set `code` strings.

### 1b. Application
- `attendance/application/ports.py` → `AttendanceRepositoryPort(Protocol)`: `get_by_employee_and_date`, `upsert(record)`, `bulk_upsert(records)`, `list_by_employee_and_date_range(employee_id, start, end)`, `list_by_business_and_date(business_id, date)`, `delete`. Plus consumer `BusinessServicePort` + `EmployeeServicePort` (copied from transaction).
- `attendance/application/services.py` → `AttendanceService` concrete gateway; thin methods + `get_or_raise`.
- `attendance/application/commands.py` (frozen dataclasses, `current_user` first):
  - `UpsertAttendanceCommand` (single), `GetAttendanceCommand`, `ListEmployeeAttendanceCommand` (year/month), `DeleteAttendanceCommand`,
  - `BulkEmployeeAttendanceCommand` (one employee, many days: `entries: list[BulkEmployeeAttendanceEntry]`),
  - `BulkBusinessAttendanceCommand` (many employees, one date: `date` + `entries: list[BulkBusinessAttendanceEntry]`).
- `attendance/application/use_cases.py`: one per op. Ownership chain `business → employee` first; bulk-many validates **every** referenced employee belongs to the business.

### 1c. Infrastructure
- `attendance/infrastructure/models.py` → `AttendanceModel(Base)` table `attendances`:
  - `id` PG_UUID PK; `employee_id` FK→employees cascade + index; `date` Date index; `status` `attendance_status_enum` (SAEnum, `values_callable`); `overtime_hours` `Numeric(6,2)` default 0; `created_at`/`updated_at` `DateTime(timezone=True)` server_default `func.now()` (+ `onupdate` for updated_at).
  - `UniqueConstraint("employee_id", "date", name="uq_attendance_employee_date")`.
  - `from_domain`/`to_domain` mappers. Define `attendance_status_enum` at module scope.
- `attendance/infrastructure/repositories.py` → `SQLAttendanceRepository`:
  - `upsert` / `bulk_upsert` via PostgreSQL `insert(...).on_conflict_do_update(index_elements=[employee_id, date])` — **justified deviation** from the simple add/flush pattern, required by PUT/full-replace + bulk semantics. (Documented in a module docstring.)

### 1d. Presentation & wiring
- `attendance/presentation/schemas.py` → `UpsertAttendanceRequest{status, overtime_hours}`, `AttendanceResponse`, `BulkEmployeeAttendanceRequest{entries[]}`, `BulkBusinessAttendanceRequest{date, entries[]}`.
- `attendance/presentation/dependencies.py` → one factory per use case (wire `AttendanceService`, `EmployeeService`, `BusinessService`, SQL repos, `uow` for writes).
- `attendance/presentation/routes.py`:
  - **employee-scoped router** (`PUT /{attendance_date}` upsert→200, `GET /{attendance_date}`, `GET ""` list w/ year+month query, `DELETE /{attendance_date}`→204, `PUT /bulk` one-employee-many-days).
  - **business-scoped router** (`PUT /bulk` many-employees-one-date — the "mark all present" path; `GET /by-date/{attendance_date}` to load current state).
- `core/router.py` → two includes:
  - `attendance_router` at `/business/{business_id}/employees/{employee_id}/attendances`, tag `attendances`.
  - `business_attendance_router` at `/business/{business_id}/attendances`, tag `attendances`.

### 1e. Migration
- `alembic/env.py`: add `from app.features.attendance.infrastructure.models import AttendanceModel  # noqa: F401`.
- `cd backend && uv run alembic revision --autogenerate -m "create attendances table"`; review the generated file (enum type, unique constraint, indexes), then `uv run alembic upgrade head`.

### 1f. Lint gate
- `cd backend && uv run ruff check && uv run ruff format --check && uv run pyright`.

---

## Milestone 2 — Payroll engine (pure Python) + unit tests
Standalone, no DB/HTTP — directly testable.

### 2a. Domain
- `payroll/domain/value_objects.py` → `PayrollStatus(StrEnum){ DRAFT="draft", FINALIZED="finalized" }`, `PayrollWarningType(StrEnum){ MISSING_ATTENDANCE="missing_attendance" }`.
- `payroll/domain/entities.py`:
  - `PayrollRun{ id, business_id, month, year, status, total_amount_due, is_warning, created_at, updated_at }` + `create(...)`, `finalize()`, `set_warning(bool)`.
  - `PayrollLineItem{ id, payroll_run_id, business_id, employee_id, employee_name, salary_type, base_rate, divisor_policy_used, overtime_multiplier_used, working_hours_used, present_days, half_days, paid_leave_days, unpaid_leave_days, holiday_days, weekly_off_days_count, overtime_hours, earned_salary, overtime_pay, total_additions, total_deductions, net_payable, status, paid_via, paid_date }` + `create(...)`.
  - `PayrollWarning{ id, payroll_line_item_id, warning_type, affected_dates, message, created_at }`.
- `payroll/domain/exceptions.py` → `PayrollRunNotFoundError`, `PayrollRunAlreadyExistsError(ConflictError)` ((business,year,month) unique), `PayrollAlreadyFinalizedError(ConflictError)`.

### 2b. Engine — `payroll/domain/services.py` (adapted from your script)
Adaptations vs. the pasted script:
- **Imports fixed to our paths**: `AttendanceStatus` from `attendance.domain.value_objects` (not `AttendanceRecordStatus`), `SalaryType` from `employee.domain.value_objects`, `WeekDay` from `app.shared.enums` (NOT redefined), `DivisorPolicy` from `business.domain.value_objects`.
- **`TransactionTotals`** → `{additions, deductions}` (replace bonuses/advances). `sum_transactions` keys on `TransactionType.ADDITION`/`DEDUCTION` (compare via `str(t.type)` or direct enum).
- **`divisor_for`** typed `DivisorPolicy | str | None`; uses `DivisorPolicy.TWENTY_SIX`/`THIRTY`/`CALENDAR`.
- Keep: `calculate_ot_pay`, `summarize_attendance`, `calculate_line_item_values`, `generate_warnings_for_line_item`, `AttendanceSummary`/`TransactionTotals` dataclasses, `_q`/`_ZERO` Decimal helpers, `_WEEKDAY_INDEX` map (computed from `WeekDay`), `__all__`.
- `net = earned + ot_pay + additions − deductions`.

### 2c. Engine unit tests
- `backend/tests/features/payroll/domain/test_services.py`: cover monthly/daily/hourly earned formulas, OT pay, divisor policies (26/30/calendar), attendance tallying (incl. holiday + weekly-off derivation), transaction summing, and `generate_warnings_for_line_item` (missing working days only; skips offs/holidays). Pure functions, no async, no DB.

---

## Milestone 3 — Payroll persistence + API
Wires the engine into the hexagonal stack.

### 3a. Application
- `payroll/application/ports.py` → `PayrollRepositoryPort` (get_run_by_id, get_by_business_and_period, add_run, add_line_items, add_warnings, list_line_items, update_run) + consumer ports: `BusinessServicePort`, `EmployeeServicePort` (`get_owned_employee` + `list_by_business`), `AttendanceServicePort` (`list_by_employee_and_date_range`), `HolidayServicePort` (`list_by_business`), `TransactionServicePort` (`get_by_employee_and_date_range` — added in M0a).
- `payroll/application/services.py` → `PayrollService` concrete gateway.
- `payroll/application/commands.py` → `CreatePayrollRunCommand{business_id, month, year}`, `GetPayrollRunCommand`, `ListPayrollRunsCommand`, `FinalizePayrollRunCommand`.
- `payroll/application/use_cases.py`:
  - **`CreatePayrollRunUseCase`** (the run-payroll orchestration, `uow`):
    1. `business = business_service.get_owned_business(...)`.
    2. reject if a run already exists for `(business, year, month)` → `PayrollRunAlreadyExistsError`.
    3. `employees = employee_service.list_by_business(business.id)` (active); `paid_holidays = holiday_service.list_by_business(business.id, year, month)` → `paid_holiday_dates` set.
    4. create `PayrollRun` (draft, `total_amount_due=0`, `is_warning=False`).
    5. per employee: fetch attendance range + transactions range → `summarize_attendance` → `sum_transactions` → `calculate_line_item_values(...)` (pass `business.divisor_policy`, employee `base_rate/salary_type/overtime_multiplier/working_hours`) → `generate_warnings_for_line_item`; set `is_warning=True` if any warning; accumulate `total_amount_due`.
    6. persist run + all line items + warnings (single transaction). Return run (+line items).
  - `FinalizePayrollRunUseCase` (draft→finalized; reject if already finalized). `GetPayrollRunUseCase`, `ListPayrollRunsCommand` (no uow).

### 3b. Infrastructure
- `payroll/infrastructure/models.py` → `PayrollRunModel` (`payroll_runs`: unique `(business_id, year, month)`), `PayrollLineItemModel` (`payroll_line_items`: FK→payroll_runs cascade, FK→employees), `PayrollWarningModel` (`payroll_warnings`: FK→payroll_line_items cascade). Money cols `Numeric(12,2)`; counts `Integer`/`Numeric`. `from_domain`/`to_domain` for each. Define `payroll_status_enum`, `payroll_warning_type_enum`.
- `payroll/infrastructure/repositories.py` → `SQLPayrollRepository`.

### 3c. Presentation & wiring
- `payroll/presentation/schemas.py` → `CreatePayrollRunRequest{month, year}`, `PayrollWarningResponse`, `PayrollLineItemResponse`, `PayrollRunResponse` (summary + nested line_items + warnings), `model_config = ConfigDict(from_attributes=True)`.
- `payroll/presentation/dependencies.py` → factories wiring `PayrollService` + the 5 cross-feature services + `uow`.
- `payroll/presentation/routes.py`:
  - `POST /business/{business_id}/payroll` → 201 (run payroll).
  - `GET /business/{business_id}/payroll` → list runs.
  - `GET /business/{business_id}/payroll/{payroll_id}` → single run (with line items + warnings).
  - `PATCH /business/{business_id}/payroll/{payroll_id}/finalize` → 200.
- `core/router.py` → include `payroll_router` at `/business/{business_id}/payroll`, tag `payroll`.

### 3d. Migration
- `alembic/env.py`: add payroll model imports (`# noqa: F401`).
- `cd backend && uv run alembic revision --autogenerate -m "create payroll tables"`; review (3 tables, FKs, unique constraint, enums); `uv run alembic upgrade head`.

---

## Milestone 4 — Verification
- `cd backend && uv run ruff check && uv run ruff format --check && uv run pyright`.
- `cd backend && uv run pytest -q` (engine unit tests).
- Smoke: `cd backend && python -c "import app.main"` and `uv run alembic check`.

---

## Notes / deviations (explicit)
- **Bulk upsert uses PG `ON CONFLICT`** in the attendance repo (not the simple add/flush used elsewhere) — required by PUT/full-replace + bulk marking; documented in-module.
- **Attendance has two routers** (employee-scoped + business-scoped) to support both bulk shapes cleanly.
- **Payroll depends on 5 features** (business/employee/attendance/holiday/transaction) via consumer-declared `Protocol` ports — consistent with the existing hexagonal convention; payroll is the top of the dependency DAG.
- **`divisor_policy` is read from `Business`** (per our model) and snapshotted onto each line item as `divisor_policy_used`.
- No `PAID` payroll status in scope yet (only draft/finalized, per the spec).

I will run lint/type/test commands from `backend/` (not the repo root) and use `uv run alembic ...` for migrations, as you specified.