"""Payroll-domain categorical values (ADR-006: StrEnum throughout)."""

from enum import StrEnum


class PayrollStatus(StrEnum):
    """Lifecycle status of a payroll run.

    A run starts in ``DRAFT`` while attendance may still be incomplete; once
    the owner is satisfied it transitions to ``FINALIZED``.
    """

    DRAFT = "draft"
    FINALIZED = "finalized"


class PayrollWarningType(StrEnum):
    """Kind of warning surfaced against a payroll line item.

    ``MISSING_ATTENDANCE`` flags working days in the payroll period that have
    no explicit attendance record (and are not weekly-off or paid-holiday days).
    """

    MISSING_ATTENDANCE = "missing_attendance"
