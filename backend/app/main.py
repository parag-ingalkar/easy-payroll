from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.core.database import get_engine
from app.shared.presentation.exception_handler import register_exception_handlers
from app.shared.presentation.router import router as shared_router


@asynccontextmanager
async def lifespan(_app: FastAPI):
    yield
    await get_engine().dispose()


app = FastAPI(lifespan=lifespan)

register_exception_handlers(app)

app.include_router(shared_router)


@app.get("/")
async def ping():
    return {"status": "ok"}
