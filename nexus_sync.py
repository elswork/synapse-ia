import os
import json
import psycopg2
from datetime import datetime

class NexusSync:
    def __init__(self, base_path=None):
        self.base_path = base_path or os.environ.get("BASE_PATH", "/app")
        self.history_path = os.path.join(self.base_path, "context/history.md")
        self.goal_path = os.path.join(self.base_path, "context/current_goal.md")
        self.db_url = os.environ.get("DATABASE_URL")

    def _get_connection(self):
        if not self.db_url:
            raise Exception("DATABASE_URL no encontrada en el entorno.")
        return psycopg2.connect(self.db_url)

    def log_event(self, agent, event_type, description, metadata=None):
        """Registra un evento en el historial (MD) y en la DB (PostgreSQL)."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        entry = f"\n## [{timestamp}] - {event_type}\n* **Agente**: {agent}\n* **Descripción**: {description}\n"
        
        # Log en Markdown
        with open(self.history_path, "a") as f:
            f.write(entry)
        
        # Log en PostgreSQL
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute("INSERT INTO events (agent, event_type, description, metadata) VALUES (%s, %s, %s, %s)",
                           (agent, event_type, description, json.dumps(metadata) if metadata else None))
            conn.commit()
            cursor.close()
            conn.close()
        except Exception as e:
            print(f"Error al registrar en DB (PostgreSQL): {e}")

        print(f"Evento registrado por {agent}")

    def update_goal(self, agent, new_goal):
        """Actualiza el objetivo prioritario en MD y DB."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        content = f"# Προτεραιότητα (Prioridad Actual)\n\n**Objetivo**: {new_goal}\n\n---\n*Actualizado por: {agent} en {timestamp}*\n"
        
        # Update en Markdown
        with open(self.goal_path, "w") as f:
            f.write(content)
        
        # Log en DB
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute("INSERT INTO goals (agent, goal) VALUES (%s, %s)", (agent, new_goal))
            conn.commit()
            cursor.close()
            conn.close()
        except Exception as e:
            print(f"Error al actualizar objetivo en DB (PostgreSQL): {e}")

        self.log_event(agent, "GOAL_UPDATE", f"Nuevo objetivo: {new_goal}")

if __name__ == "__main__":
    # Test simple
    syncer = NexusSync()
    print("Nexus Syncer inicializado para PostgreSQL.")
