from enum import StrEnum


class TransactionType(StrEnum):
    """Direction of a transaction against an employee's payroll.

    ADDITION increases the payable amount; DEDUCTION decreases it. The
    transaction ``amount`` is always stored strictly positive — the direction
    is encoded by this enum, never by the sign of the amount.
    """

    ADDITION = "addition"
    DEDUCTION = "deduction"
