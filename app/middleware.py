"""Middleware для FastAPI приложения."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


def setup_cors(app: FastAPI) -> None:
    """Настройка CORS middleware."""
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # В продакшене нужно указать конкретные домены
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
