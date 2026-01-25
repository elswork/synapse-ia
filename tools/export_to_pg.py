import sqlite3
import json
import os

def export_sqlite_to_json(db_path="context/synapse_memory.db", output_dir="tools/migration_data"):
    if not os.path.exists(db_path):
        print(f"Error: No se encontró la base de datos en {db_path}")
        return

    os.makedirs(output_dir, exist_ok=True)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    tables = ["citizens", "events", "goals"]
    
    for table in tables:
        cursor.execute(f"SELECT * FROM {table}")
        # Obtener nombres de columnas
        columns = [column[0] for column in cursor.description]
        rows = cursor.fetchall()
        
        data = []
        for row in rows:
            data.append(dict(zip(columns, row)))
        
        output_file = os.path.join(output_dir, f"{table}.json")
        with open(output_file, 'w') as f:
            json.dump(data, f, indent=4)
        
        print(f"Exportada tabla {table} ({len(rows)} registros) a {output_file}")

    conn.close()

if __name__ == "__main__":
    export_sqlite_to_json()
