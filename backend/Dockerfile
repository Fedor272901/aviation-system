FROM python:3.12-slim AS production

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# ENV PATH=/root/.local/bin:$PATH

RUN apt-get update && \
  apt-get install -y --no-install-recommends \
  gnupg2 \
  unixodbc \
  ca-certificates && \
  rm -rf /var/lib/apt/lists/*

# Зеркала Yandex для Debian + установка всего за один проход
RUN set -eux; \
  sed -i 's|http://deb.debian.org|http://mirror.yandex.ru|g' /etc/apt/sources.list.d/debian.sources && \
  apt-get update && \
  apt-get install -y --no-install-recommends \
    curl \
    gnupg2 \
    gcc \
    g++ \
    unixodbc-dev \
  && \
  curl -fsSL https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor -o /usr/share/keyrings/microsoft-prod.gpg && \
  curl https://packages.microsoft.com/config/debian/12/prod.list | tee /etc/apt/sources.list.d/mssql-release.list && \
  apt-get update && \
  ACCEPT_EULA=Y apt-get install -y msodbcsql18 unixodbc && \
  apt-get purge -y --auto-remove gcc g++ unixodbc-dev && \
  rm -rf /var/lib/apt/lists/* && \
  apt-get clean

# RUN set -eux; \
#   apt-get update; \
#   apt-get install -y curl; \
#   curl -fsSL https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor -o /usr/share/keyrings/microsoft-prod.gpg; \
#   curl https://packages.microsoft.com/config/debian/12/prod.list > /etc/apt/sources.list.d/mssql-release.list; \
#   apt-get update; \
#   ACCEPT_EULA=Y apt-get install -y msodbcsql18; \
#   apt-get purge -y --auto-remove curl; \
#   rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ ./app/
COPY alembic/ ./alembic/
COPY alembic.ini ./
COPY pytest.ini ./
COPY docker-entrypoint.sh ./

RUN chmod +x ./docker-entrypoint.sh

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=30s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')"

ENTRYPOINT ["./docker-entrypoint.sh"]