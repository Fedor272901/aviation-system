# =========================================================
# STAGE 1: Build frontend
# =========================================================
FROM node:20-alpine AS frontend-builder

WORKDIR /app/frontend
COPY frontend/package.json frontend/package-lock.json* ./
RUN npm ci
COPY frontend/ ./
RUN npm run build

# =========================================================
# STAGE 2: Python + ODBC + App
# =========================================================
FROM python:3.12-slim AS production

WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PATH=/root/.local/bin:$PATH

# Зеркала Yandex для Debian + установка всего за один проход
RUN set -eux; \
  # Настройка зеркал
  sed -i 's|http://deb.debian.org|http://mirror.yandex.ru|g' /etc/apt/sources.list.d/debian.sources && \
  \
  # Установка зависимостей
  apt-get update && \
  apt-get install -y --no-install-recommends \
  curl \
  gnupg2 \
  gcc \
  g++ \
  unixodbc-dev \
  && \
  # Microsoft ODBC Driver 18
  curl -fsSL https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor -o /usr/share/keyrings/microsoft-prod.gpg && \
  curl https://packages.microsoft.com/config/debian/12/prod.list | tee /etc/apt/sources.list.d/mssql-release.list && \
  apt-get update && \
  ACCEPT_EULA=Y apt-get install -y msodbcsql18 unixodbc && \
  \
  # Очистка
  apt-get purge -y --auto-remove gcc g++ unixodbc-dev && \
  rm -rf /var/lib/apt/lists/* && \
  apt-get clean

# Python зависимости
COPY requirements.txt ./
RUN pip install --no-cache-dir --user -r requirements.txt

# Код приложения
COPY app/ ./app/
COPY alembic/ ./alembic/
COPY alembic.ini ./
COPY pytest.ini ./
COPY docker-entrypoint.sh ./
# COPY scripts/ ./scripts/

RUN chmod +x ./docker-entrypoint.sh

# Статика из фронтенда
COPY --from=frontend-builder /app/frontend/dist/ ./static/

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=30s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

ENTRYPOINT ["./docker-entrypoint.sh"]