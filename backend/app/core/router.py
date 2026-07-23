from fastapi import APIRouter

from app.features.auth.presentation.routes import router as auth_router
from app.features.business.presentation.routes import router as business_router
from app.features.employee.presentation.routes import router as employee_router
from app.features.holiday.presentation.routes import router as holiday_router
from app.features.transaction.presentation.routes import router as transaction_router

router = APIRouter(prefix="/api")

router.include_router(auth_router, tags=["auth"])
router.include_router(business_router, prefix="/business", tags=["business"])
router.include_router(
    employee_router, tags=["employees"]
)
router.include_router(holiday_router, prefix="/business/{business_id}/holidays", tags=["holidays"])
router.include_router(
    transaction_router,
    prefix="/business/{business_id}/employees/{employee_id}/transactions",
    tags=["transactions"],
)
