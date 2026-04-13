import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()
DB_PASSWORD = os.environ.get("DB_PASSWORD")
DATABASE_URL = os.environ.get("DATABASE_URL", f"postgresql://arconte:{DB_PASSWORD}@db:5432/synapse_ia")

try:
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    
    print("--- Verificando esquema ---")
    cursor.execute("SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'news_intel';")
    for row in cursor.fetchall():
        print(f"Columna: {row[0]}, Tipo: {row[1]}")
    
    print("\n--- Limpiando tabla news_intel ---")
    cursor.execute("TRUNCATE TABLE news_intel;")
    conn.commit()
    print("Tabla limpia con éxito.")
    
    cursor.close()
    conn.close()
except Exception as e:
    print(f"Error: {e}")
