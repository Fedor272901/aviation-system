import logging
import time
from fastapi import Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.core.config import get_settings

settings = get_settings()
logger = logging.getLogger(__name__)


def setup_cors(app):
    """Настройка CORS."""
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


async def log_requests(request: Request, call_next):
    """Логирование запросов."""
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time

    logger.info(
        f"{request.method} {request.url.path} "
        f"status={response.status_code} time={process_time:.3f}s"
    )

    return response


async def handle_exceptions(app, call_next):
    """Глобальная обработка ошибок."""
    try:
        return await call_next(app)
    except Exception as exc:
        logger.error(f"Unhandled error: {exc}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={"detail": "Внутренняя ошибка сервера", "path": str(app.url.path)}
        )