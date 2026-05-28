#!/bin/sh
set -e

echo "▶️  Проверка подключения к MSSQL..."
python << 'EOF'
import os
import time
import re
import pyodbc
from urllib.parse import urlparse

db_url = os.getenv('DATABASE_URL', '')
db_name_env = os.getenv('APP_DB_NAME', '').strip()
db_collation = os.getenv('APP_DB_COLLATION', 'Cyrillic_General_CI_AS').strip()

match = re.match(r'mssql\+pyodbc://([^:]+):([^@]+)@([^/]+)/.*', db_url)
if not match:
    print('❌ Не удалось распарсить DATABASE_URL')
    exit(1)

user = match.group(1)
password = match.group(2).replace('%40', '@')
host_port = match.group(3)
server = host_port.replace(':', ',')

parsed = urlparse(db_url.replace("mssql+pyodbc://", "http://", 1))
db_name = db_name_env or parsed.path.lstrip('/').split('?')[0] or 'AviationDB'

print(f'🔗 Подключение к {server} как {user}')
print(f'🗄️ Целевая БД: {db_name} (collation={db_collation})')

conn_str = (
    f"DRIVER={{ODBC Driver 18 for SQL Server}};"
    f"SERVER={server};"
    f"DATABASE=master;"
    f"UID={user};"
    f"PWD={password};"
    f"Encrypt=yes;"
    f"TrustServerCertificate=yes;"
)

for i in range(30):
    try:
        conn = pyodbc.connect(conn_str, timeout=10)
        conn.autocommit = True
        cursor = conn.cursor()
        cursor.execute(f"SELECT COUNT(*) FROM sys.databases WHERE name = N'{db_name}'")
        exists = cursor.fetchone()[0]
        if not exists:
            cursor.execute(f"CREATE DATABASE [{db_name}] COLLATE {db_collation}")
            print(f'✅ База {db_name} создана ({db_collation})')
        else:
            print(f'✅ База {db_name} уже существует')
        cursor.close()
        conn.close()
        break
    except Exception as e:
        print(f'⏳ Ожидание MSSQL... ({e})')
        time.sleep(2)
else:
    print('❌ Не удалось подключиться к MSSQL')
    exit(1)
EOF

echo "▶️  Запуск миграций Alembic..."
alembic upgrade head

echo "▶️  Заполнение справочников..."
python -c "
from app.db import SessionLocal
from app.seed_data import seed_database
db = SessionLocal()
try:
    seed_database(db)
    print('✅ Справочники проверены')
except Exception as e:
    print(f'⚠️  Ошибка seed: {e}')
finally:
    db.close()
"

echo "▶️  Проверка/создание admin..."
python -m app.scripts.ensure_admin

echo "▶️  Запуск приложения..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --proxy-headers