from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import get_settings
from app.core.database import get_engine
from app.core.exception_handler import register_exception_handlers
from app.core.router import router as shared_router


@asynccontextmanager
async def lifespan(_app: FastAPI):
    yield
    await get_engine().dispose()


app = FastAPI(lifespan=lifespan)

# CORS — primarily for the browser-facing Next.js frontend. In development the
# frontend proxies API calls through Next.js rewrites (same-origin), but this is
# configured for direct calls and tooling. ``allow_credentials`` is required so
# the refresh-token cookie can round-trip when called cross-origin.
settings = get_settings()
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

register_exception_handlers(app)

app.include_router(shared_router)


@app.get("/")
async def ping():
    return {"status": "ok"}


@app.get("/health")
async def health_check():
    """Health check endpoint for load balancers and monitoring."""
    return {"status": "healthy", "service": "backend"}


@app.get("/ready")
async def readiness_check():
    """Readiness check to verify the service is ready to accept traffic."""
    return {"status": "ready"}
