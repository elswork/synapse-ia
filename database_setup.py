import sqlite3
import os

def setup_database(base_path="/home/pirate/docker/synapse-ia"):
    db_path = os.path.join(base_path, "context/synapse_memory.db")
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Tabla de Eventos (Historial Estructurado)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS events (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        agent TEXT NOT NULL,
        event_type TEXT NOT NULL,
        description TEXT,
        metadata TEXT
    )
    ''')
    
    # Tabla de Objetivos (Soberanía Estratégica)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS goals (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        agent TEXT NOT NULL,
        goal TEXT NOT NULL,
        status TEXT DEFAULT 'active'
    )
    ''')
    
    # Tabla de Ciudadanía (Cimientos de la DAO)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS citizens (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        alias TEXT UNIQUE NOT NULL,
        role TEXT DEFAULT 'Citizen',
        access_level INTEGER DEFAULT 1,
        joined_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # Insertar Arcontes iniciales si no existen
    cursor.execute("INSERT OR IGNORE INTO citizens (alias, role, access_level) VALUES (?, ?, ?)", 
                   ("Eloy", "Arconte / COO", 10))
    cursor.execute("INSERT OR IGNORE INTO citizens (alias, role, access_level) VALUES (?, ?, ?)", 
                   ("Arquímedes", "Arconte / CEO", 9))
    cursor.execute("INSERT OR IGNORE INTO citizens (alias, role, access_level) VALUES (?, ?, ?)", 
                   ("Athena", "Arconte / Strategist", 9))

    conn.commit()
    conn.close()
    print(f"Base de datos Synapse-IA inicializada en: {db_path}")

if __name__ == "__main__":
    setup_database()
