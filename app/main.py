from contextlib import asynccontextmanager
import logging
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from app.routers import person, flight, aircraft, crew, ticket
from app.middleware import setup_cors
from app.core.config import get_settings

settings = get_settings()

# Настройка логирования
logging.basicConfig(
    level=logging.INFO if settings.DEBUG else logging.WARNING,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    if settings.DEBUG:
        # Только для локальной разработки без Alembic.
        # В production таблицы управляются миграциями!
        from app.db import create_tables

        create_tables()
        logger.info("Таблицы созданы (DEBUG-режим)")
    logger.info("Приложение запущено")
    yield
    logger.info("Приложение остановлено")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.VERSION,
    description="Система управления авиаперевозками",
    lifespan=lifespan,
)

# CORS middleware
setup_cors(app)


# Middleware: логирование запросов
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


# Middleware: глобальная обработка ошибок
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled error: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Внутренняя ошибка сервера", "path": str(request.url.path)},
    )


# Роутеры
app.include_router(person.router, prefix="/api/v1")
app.include_router(flight.router, prefix="/api/v1")
app.include_router(aircraft.router, prefix="/api/v1")
app.include_router(crew.router, prefix="/api/v1")
app.include_router(ticket.router, prefix="/api/v1")


@app.get("/")
def root():
    return {"message": settings.APP_NAME, "version": settings.VERSION}


@app.get("/health")
def health_check():
    return {"status": "healthy"}


from fastapi.staticfiles import StaticFiles

app.mount("/", StaticFiles(directory="static", html=True), name="static")


# Для запуска через uvicorn в консоли
if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=settings.DEBUG)
