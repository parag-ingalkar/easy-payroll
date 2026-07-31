"""Payroll API routes.

All endpoints are business-scoped, mounted at
``/business/{business_id}/payroll`` in ``app/core/router.py``:

* ``POST /`` → run payroll for a (year, month); 201.
* ``GET /`` → list runs (summary only).
* ``GET /{payroll_id}`` → single run with nested line items + warnings.
* ``PATCH /{payroll_id}/finalize`` → transition a run to FINALIZED.
"""

from uuid import UUID

from fastapi import APIRouter, Depends, status

from app.features.auth.domain.entities import CurrentUser
from app.features.auth.presentation.dependencies import get_current_user
from app.features.payroll.application.commands import (
    CreatePayrollRunCommand,
    FinalizePayrollRunCommand,
    GetPayrollRunCommand,
    ListPayrollRunsCommand,
    MarkAllPaidCommand,
    MarkLineItemPaidCommand,
)
from app.features.payroll.application.use_cases import (
    CreatePayrollRunUseCase,
    FinalizePayrollRunUseCase,
    GetPayrollRunUseCase,
    ListPayrollRunsUseCase,
    MarkAllPaidUseCase,
    MarkLineItemPaidUseCase,
)
from app.features.payroll.presentation.dependencies import (
    get_create_payroll_run_use_case,
    get_finalize_payroll_run_use_case,
    get_get_payroll_run_use_case,
    get_list_payroll_runs_use_case,
    get_mark_all_paid_use_case,
    get_mark_line_item_paid_use_case,
)
from app.features.payroll.presentation.schemas import (
    CreatePayrollRunRequest,
    MarkPaidRequest,
    PayrollLineItemResponse,
    PayrollRunResponse,
    PayrollWarningResponse,
)

router = APIRouter()


def _build_run_response(run, line_items=(), warnings=()) -> PayrollRunResponse:
    """Build a ``PayrollRunResponse`` with nested line items, warnings, and is_paid."""
    from app.features.payroll.domain.value_objects import PayrollStatus

    response = PayrollRunResponse.model_validate(run)
    response.line_items = [PayrollLineItemResponse.model_validate(li) for li in line_items]
    response.warnings = [PayrollWarningResponse.model_validate(w) for w in warnings]
    response.is_paid = bool(response.line_items) and all(
        li.status == PayrollStatus.PAID for li in response.line_items
    )
    return response


@router.post("", response_model=PayrollRunResponse, status_code=status.HTTP_201_CREATED)
async def create_payroll_run(
    business_id: UUID,
    body: CreatePayrollRunRequest,
    current_user: CurrentUser = Depends(get_current_user),
    use_case: CreatePayrollRunUseCase = Depends(get_create_payroll_run_use_case),
) -> PayrollRunResponse:
    """Compute and persist a payroll run for a business for a (year, month)."""
    command = CreatePayrollRunCommand(
        current_user=current_user,
        business_id=business_id,
        month=body.month,
        year=body.year,
    )
    result = await use_case.execute(command)
    return _build_run_response(result.run, result.line_items, result.warnings)


@router.get("", response_model=list[PayrollRunResponse])
async def list_payroll_runs(
    business_id: UUID,
    current_user: CurrentUser = Depends(get_current_user),
    use_case: ListPayrollRunsUseCase = Depends(get_list_payroll_runs_use_case),
) -> list[PayrollRunResponse]:
    """List payroll runs for a business (summary only; most recent first)."""
    command = ListPayrollRunsCommand(current_user=current_user, business_id=business_id)
    runs = await use_case.execute(command)
    return [PayrollRunResponse.model_validate(run) for run in runs]


@router.get("/{payroll_id}", response_model=PayrollRunResponse)
async def get_payroll_run(
    business_id: UUID,
    payroll_id: UUID,
    current_user: CurrentUser = Depends(get_current_user),
    use_case: GetPayrollRunUseCase = Depends(get_get_payroll_run_use_case),
) -> PayrollRunResponse:
    """Fetch a single run with its nested line items and warnings."""
    command = GetPayrollRunCommand(
        current_user=current_user,
        business_id=business_id,
        payroll_id=payroll_id,
    )
    result = await use_case.execute(command)
    return _build_run_response(result.run, result.line_items, result.warnings)


@router.patch("/{payroll_id}/finalize", response_model=PayrollRunResponse)
async def finalize_payroll_run(
    business_id: UUID,
    payroll_id: UUID,
    current_user: CurrentUser = Depends(get_current_user),
    use_case: FinalizePayrollRunUseCase = Depends(get_finalize_payroll_run_use_case),
) -> PayrollRunResponse:
    """Transition a payroll run from DRAFT to FINALIZED."""
    command = FinalizePayrollRunCommand(
        current_user=current_user,
        business_id=business_id,
        payroll_id=payroll_id,
    )
    run = await use_case.execute(command)
    return PayrollRunResponse.model_validate(run)


@router.patch(
    "/{payroll_id}/line-items/{line_item_id}/pay",
    response_model=PayrollRunResponse,
)
async def mark_line_item_paid(
    business_id: UUID,
    payroll_id: UUID,
    line_item_id: UUID,
    body: MarkPaidRequest,
    current_user: CurrentUser = Depends(get_current_user),
    use_case: MarkLineItemPaidUseCase = Depends(get_mark_line_item_paid_use_case),
) -> PayrollRunResponse:
    """Mark a single payroll line item as paid."""
    from datetime import date as date_type

    command = MarkLineItemPaidCommand(
        current_user=current_user,
        business_id=business_id,
        payroll_id=payroll_id,
        line_item_id=line_item_id,
        paid_via=body.paid_via,
        paid_date=body.paid_date or date_type.today(),
    )
    result = await use_case.execute(command)
    return _build_run_response(result.run, result.line_items, result.warnings)


@router.patch("/{payroll_id}/pay-all", response_model=PayrollRunResponse)
async def mark_all_paid(
    business_id: UUID,
    payroll_id: UUID,
    body: MarkPaidRequest,
    current_user: CurrentUser = Depends(get_current_user),
    use_case: MarkAllPaidUseCase = Depends(get_mark_all_paid_use_case),
) -> PayrollRunResponse:
    """Mark every line item in a payroll run as paid."""
    from datetime import date as date_type

    command = MarkAllPaidCommand(
        current_user=current_user,
        business_id=business_id,
        payroll_id=payroll_id,
        paid_via=body.paid_via,
        paid_date=body.paid_date or date_type.today(),
    )
    result = await use_case.execute(command)
    return _build_run_response(result.run, result.line_items, result.warnings)
