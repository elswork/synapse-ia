import psycopg2
import os
from dotenv import load_dotenv

def run_migration():
    load_dotenv()
    DB_PASSWORD = os.environ.get("DB_PASSWORD")
    DATABASE_URL = os.environ.get("DATABASE_URL", f"postgresql://arconte:{DB_PASSWORD}@db:5432/synapse_ia")

    try:
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()
        
        # print("--- Limpiando noticias existentes ---")
        # cursor.execute("TRUNCATE TABLE news_intel CASCADE;")
        
        print("--- Añadiendo columna is_approved ---")
        cursor.execute("""
            SELECT count(*) FROM information_schema.columns 
            WHERE table_name='news_intel' AND column_name='is_approved';
        """)
        if cursor.fetchone()[0] == 0:
            cursor.execute("ALTER TABLE news_intel ADD COLUMN is_approved BOOLEAN DEFAULT FALSE;")
            print("Columna 'is_approved' añadida.")
        else:
            print("La columna 'is_approved' ya existe.")
        
        conn.commit()
        print("Operación completada con éxito.")
        
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Error en run_migration: {e}")

if __name__ == "__main__":
    run_migration()
