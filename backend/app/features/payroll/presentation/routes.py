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
)
from app.features.payroll.application.use_cases import (
    CreatePayrollRunUseCase,
    FinalizePayrollRunUseCase,
    GetPayrollRunUseCase,
    ListPayrollRunsUseCase,
)
from app.features.payroll.presentation.dependencies import (
    get_create_payroll_run_use_case,
    get_finalize_payroll_run_use_case,
    get_get_payroll_run_use_case,
    get_list_payroll_runs_use_case,
)
from app.features.payroll.presentation.schemas import (
    CreatePayrollRunRequest,
    PayrollLineItemResponse,
    PayrollRunResponse,
    PayrollWarningResponse,
)

router = APIRouter()


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
    response = PayrollRunResponse.model_validate(result.run)
    response.line_items = [PayrollLineItemResponse.model_validate(li) for li in result.line_items]
    response.warnings = [PayrollWarningResponse.model_validate(w) for w in result.warnings]
    return response


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
    response = PayrollRunResponse.model_validate(result.run)
    response.line_items = [PayrollLineItemResponse.model_validate(li) for li in result.line_items]
    response.warnings = [PayrollWarningResponse.model_validate(w) for w in result.warnings]
    return response


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
