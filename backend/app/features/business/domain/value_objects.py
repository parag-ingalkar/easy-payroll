"""Business-domain categorical values (ADR-006: StrEnum throughout).

``WeekDay`` is duplicated in the employee domain (each domain is an isolated
vertical slice per ARCHITECTURE.md). Both definitions are value-identical
StrEnums, so cross-domain assignment works via string coercion.
"""

from enum import StrEnum


class DivisorPolicy(StrEnum):
    """Monthly-salary divisor policy (PRODUCT.md → DivisorPolicy)."""

    TWENTY_SIX = "26"
    THIRTY = "30"
    CALENDAR = "calendar"
