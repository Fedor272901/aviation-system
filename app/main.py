from contextlib import asynccontextmanager
import logging
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy import text
from app.db import engine, SessionLocal
from app.routers import person, flight, aircraft, crew, ticket, auth
from app.middleware import setup_cors
from app.core.config import get_settings
from app.core.logging_config import setup_logging
from app.seed_data import seed_database

settings = get_settings()

setup_logging(level=logging.INFO if settings.DEBUG else logging.WARNING)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    if settings.DEBUG:
        from app.db import SessionLocal
        seed_database(SessionLocal())
        logger.info("Seed-данные загружены (DEBUG-режим)")

    logger.info("Приложение запущено")
    yield

    # ✅ Graceful shutdown: закрываем пул соединений
    engine.dispose()
    logger.info("Приложение остановлено, соединения с БД закрыты")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.VERSION,
    description="Система управления авиаперевозками",
    lifespan=lifespan,
)

setup_cors(app)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    import time
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    logger.info(
        f"{request.method} {request.url.path} status={response.status_code} time={process_time:.3f}s"
    )
    return response


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled error: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Внутренняя ошибка сервера", "path": str(request.url.path)},
    )


app.include_router(person.router, prefix="/api/v1")
app.include_router(flight.router, prefix="/api/v1")
app.include_router(aircraft.router, prefix="/api/v1")
app.include_router(crew.router, prefix="/api/v1")
app.include_router(ticket.router, prefix="/api/v1")
app.include_router(auth.router, prefix="/api/v1")


@app.get("/health")
def health_check():
    """✅ Расширенная проверка: API + БД"""
    try:
        with SessionLocal() as db:
            db.execute(text("SELECT 1"))
        return {
            "status": "healthy",
            "database": "connected",
            "version": settings.VERSION,
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return JSONResponse(
            status_code=503,
            content={"status": "unhealthy", "database": "disconnected", "error": str(e)},
        )


app.mount("/", StaticFiles(directory="static", html=True), name="static")


@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    if request.url.path.startswith("/api/") or request.url.path == "/health":
        return JSONResponse(status_code=404, content={"detail": "Not Found"})
    return FileResponse("static/index.html")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=settings.DEBUG)