import pyodbc

conn = pyodbc.connect(
    "DRIVER={ODBC Driver 18 for SQL Server};"
    "SERVER=172.17.160.1,1433;"
    "DATABASE=WSL_AIRLINE;"
    "UID=sa;"
    "PWD=StrongPassword123!;"
    "Encrypt=no;"
    "TrustServerCertificate=yes;"
)

print("CONNECTED")
