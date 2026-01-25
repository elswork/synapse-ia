import json
import os
import psycopg2
from psycopg2.extras import execute_values

def load_json_to_pg():
    db_url = os.environ.get("DATABASE_URL")
    if not db_url:
        print("Error: DATABASE_URL no encontrada en el entorno.")
        return

    migration_dir = "tools/migration_data"
    tables = ["citizens", "events", "goals"]
    
    try:
        conn = psycopg2.connect(db_url)
        cursor = conn.cursor()
        
        # Primero inicializamos el esquema
        schema_path = "tools/schema_postgres.sql"
        if os.path.exists(schema_path):
            with open(schema_path, 'r') as f:
                cursor.execute(f.read())
            print("Esquema PostgreSQL inicializado.")

        for table in tables:
            json_file = os.path.join(migration_dir, f"{table}.json")
            if not os.path.exists(json_file):
                print(f"Aviso: No se encontró el archivo {json_file}, saltando...")
                continue
            
            with open(json_file, 'r') as f:
                data = json.load(f)
            
            if not data:
                continue

            # Obtener columnas
            columns = data[0].keys()
            # Filtrar 'id' si es serial en PG
            query_cols = [c for c in columns if c != "id"]
            
            # Preparar valores
            values = [tuple(row[c] for c in query_cols) for row in data]

            insert_query = f"INSERT INTO {table} ({', '.join(query_cols)}) VALUES %s ON CONFLICT (alias) DO NOTHING" if table == "citizens" else f"INSERT INTO {table} ({', '.join(query_cols)}) VALUES %s"
            
            execute_values(cursor, insert_query, values)
            print(f"Cargados {len(data)} registros en la tabla {table}.")

        conn.commit()
        cursor.close()
        conn.close()
        print("Migración a PostgreSQL completada con éxito.")

    except Exception as e:
        print(f"Error durante la carga: {e}")

if __name__ == "__main__":
    load_json_to_pg()
