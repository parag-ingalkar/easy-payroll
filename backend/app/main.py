from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import JSONResponse

from app.core.database import get_engine
from app.features.auth.domain.exceptions import (
    InvalidCredentialsError,
    InvalidTokenError,
    UserAlreadyExists,
)
from app.features.auth.presentation.routes import router as auth_router


@asynccontextmanager
async def lifespan(_app: FastAPI):
    yield
    await get_engine().dispose()


app = FastAPI(lifespan=lifespan)

app.include_router(auth_router)


@app.exception_handler(UserAlreadyExists)
async def user_already_exists_handler(_request, exc: UserAlreadyExists):
    return JSONResponse(status_code=409, content={"detail": str(exc)})


@app.exception_handler(InvalidCredentialsError)
async def invalid_credentials_handler(_request, exc: InvalidCredentialsError):
    return JSONResponse(status_code=401, content={"detail": str(exc)})


@app.exception_handler(InvalidTokenError)
async def invalid_token_handler(_request, exc: InvalidTokenError):
    return JSONResponse(status_code=401, content={"detail": str(exc)})


@app.get("/")
async def ping():
    return {"status": "ok"}
