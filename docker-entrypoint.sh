#!/bin/sh
set -e

echo "▶️  Проверка подключения к MSSQL..."
python << 'EOF'
import os
import time
import re
import pyodbc

db_url = os.getenv('DATABASE_URL', '')
match = re.match(r'mssql\+pyodbc://([^:]+):([^@]+)@([^/]+)/.*', db_url)
if not match:
    print('❌ Не удалось распарсить DATABASE_URL')
    exit(1)

user = match.group(1)
password = match.group(2).replace('%40', '@')
host_port = match.group(3)
server = host_port.replace(':', ',')

print(f'🔗 Подключение к {server} как {user}')

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
        cursor.execute("SELECT COUNT(*) FROM sys.databases WHERE name = N'AviationDB'")
        exists = cursor.fetchone()[0]
        if not exists:
            cursor.execute("CREATE DATABASE AviationDB COLLATE Cyrillic_General_CI_AS")
            print('✅ База AviationDB создана (Cyrillic_General_CI_AS)')
        else:
            print('✅ База AviationDB уже существует')
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

echo "▶️  Запуск приложения..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --proxy-headers