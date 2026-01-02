# server/app/main.py
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.endpoints import router as api_router


def create_app() -> FastAPI:
    app = FastAPI(
        title="Quote API",
        version="0.1.0",
    )

    allowed_origins = os.getenv(
        "ALLOWED_ORIGINS",
        "http://localhost:3000",
    ).split(",")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=[origin.strip() for origin in allowed_origins],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(api_router)

    return app


app = create_app()
