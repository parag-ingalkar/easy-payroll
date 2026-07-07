from fastapi import APIRouter

from app.features.auth.presentation.routes import router as auth_router

router = APIRouter(prefix="/api")

router.include_router(auth_router, tags=["auth"])
