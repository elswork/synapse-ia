import psycopg2
import os
from dotenv import load_dotenv

# Cargar variables de entorno del Nexus
load_dotenv("/home/pirate/docker/synapse-ia/.env")

def list_todos():
    try:
        # Usar la DATABASE_URL del .env
        db_url = os.environ.get("DATABASE_URL")
        if not db_url:
            print("Error: DATABASE_URL no encontrada.")
            return

        conn = psycopg2.connect(db_url)
        cur = conn.cursor()
        
        cur.execute("SELECT id, timestamp, description, status FROM todos WHERE status != 'completed' ORDER BY id ASC;")
        rows = cur.fetchall()
        
        if not rows:
            print("\n--- LA LISTA DE POSTGRES ESTÁ VACÍA O TODAS LAS TAREAS ESTÁN COMPLETADAS ---")
        else:
            print(f"\n--- LISTA DE TAREAS PENDIENTES (POSTGRES) ---")
            for row in rows:
                id_task, timestamp, desc, status = row
                print(f"[{id_task}] {timestamp.strftime('%Y-%m-%d %H:%M')} | {status.upper()} | {desc}")
        
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Error al conectar con la base de datos: {e}")

if __name__ == "__main__":
    list_todos()
