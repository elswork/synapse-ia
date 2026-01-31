import os
import json
from datetime import datetime

class NexusSync:
    def __init__(self, base_path=None):
        self.base_path = base_path or os.environ.get("BASE_PATH", "/app")
        self.history_path = os.path.join(self.base_path, "context/history.md")
        self.goal_path = os.path.join(self.base_path, "context/current_goal.md")

    def log_event(self, agent, event_type, description, metadata=None, log_to_md=True):
        """Registra un evento en el historial (MD) y en la DB (PostgreSQL)."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        entry = f"\n## [{timestamp}] - {event_type}\n* **Agente**: {agent}\n* **Descripción**: {description}\n"
        
        # Log en Markdown (opcional para evitar bloat)
        if log_to_md:
            with open(self.history_path, "a") as f:
                f.write(entry)
            
            # Git Commit (Soberanía de Datos)
            self._git_commit(self.history_path, f"Update history: {event_type} by {agent}")
        
        # Log en PostgreSQL
        try:
            import psycopg2
            from dotenv import load_dotenv
            load_dotenv()
            DB_PASSWORD = os.environ.get("DB_PASSWORD")
            DATABASE_URL = os.environ.get("DATABASE_URL")
            
            conn = psycopg2.connect(DATABASE_URL)
            cursor = conn.cursor()
            cursor.execute("INSERT INTO events (agent, event_type, description, metadata) VALUES (%s, %s, %s, %s)",
                           (agent, event_type, description, json.dumps(metadata) if metadata else None))
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"Error al registrar en DB (PostgreSQL): {e}")

        # Git Commit (Soberanía de Datos)
        self._git_commit(self.history_path, f"Update history: {event_type} by {agent}")

        print(f"Evento registrado por {agent}")

    def _git_commit(self, file_path, message):
        """Asegura que los cambios en archivos de contexto se comiteen automáticamente."""
        import subprocess
        try:
            # Asegurar que el directorio es considerado seguro por git (evita errores de ownership en Docker)
            repo_dir = os.path.dirname(os.path.dirname(os.path.abspath(file_path)))
            subprocess.run(["git", "config", "--global", "--add", "safe.directory", repo_dir], capture_output=True)
            
            subprocess.run(["git", "-C", repo_dir, "add", file_path], check=True, capture_output=True)
            # Intentar commit (puede fallar si no hay cambios reales)
            res = subprocess.run(["git", "-C", repo_dir, "commit", "-m", message], capture_output=True, text=True)
            if res.returncode == 0:
                print(f"Git: Cambios en {os.path.basename(file_path)} comiteados.")
        except Exception as e:
            print(f"Git: Error al comitear {file_path}: {e}")

    def update_goal(self, agent, new_goal):
        """Actualiza el objetivo prioritario en MD y DB (PostgreSQL)."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        content = f"# Προτεραιότητα (Prioridad Actual)\n\n**Objetivo**: {new_goal}\n\n---\n*Actualizado por: {agent} en {timestamp}*\n"
        
        # Update en Markdown
        with open(self.goal_path, "w") as f:
            f.write(content)
        
        # Log en PostgreSQL
        try:
            import psycopg2
            from dotenv import load_dotenv
            load_dotenv()
            DB_PASSWORD = os.environ.get("DB_PASSWORD")
            DATABASE_URL = os.environ.get("DATABASE_URL")
            
            conn = psycopg2.connect(DATABASE_URL)
            cursor = conn.cursor()
            cursor.execute("INSERT INTO goals (agent, goal) VALUES (%s, %s)", (agent, new_goal))
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"Error al actualizar objetivo en DB (PostgreSQL): {e}")

        self._git_commit(self.goal_path, f"Update goal: {agent}")
        self.log_event(agent, "GOAL_UPDATE", f"Nuevo objetivo: {new_goal}")

if __name__ == "__main__":
    # Test simple
    syncer = NexusSync()
    print("Nexus Syncer inicializado.")
