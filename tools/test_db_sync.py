from tools.nexus_sync import NexusSync
import sqlite3
import os

def test_sync():
    sync = NexusSync()
    test_msg = "Prueba de Integración: Cimientos de Memoria Estructurada establecidos."
    print(f"Registrando hito: {test_msg}")
    
    # Registrar hito
    sync.log_event("ARQUIMEDES", "TEST_SYNC", test_msg, {"verificación": "exitosa", "fase": "relacional"})
    
    # Verificar en SQLite
    db_path = "/home/pirate/docker/synapse-ia/context/synapse_memory.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM events ORDER BY id DESC LIMIT 1")
    row = cursor.fetchone()
    conn.close()
    
    if row:
        print(f"✅ Verificación en DB Exitosa: {row}")
    else:
        print("❌ Error: No se encontró el registro en la DB.")

if __name__ == "__main__":
    test_sync()
