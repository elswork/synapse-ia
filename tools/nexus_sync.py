import os
import json
from datetime import datetime

class NexusSync:
    def __init__(self, base_path="/home/pirate/docker/synapse-ia"):
        self.base_path = base_path
        self.history_path = os.path.join(base_path, "context/history.md")
        self.goal_path = os.path.join(base_path, "context/current_goal.md")

    def log_event(self, agent, event_type, description):
        """Registra un evento en el historial siguiendo el estándar [AGENTE]."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        entry = f"\n## [{timestamp}] - {event_type}\n* **Agente**: {agent}\n* **Descripción**: {description}\n"
        
        with open(self.history_path, "a") as f:
            f.write(entry)
        print(f"Evento registrado por {agent}")

    def update_goal(self, agent, new_goal):
        """Actualiza el objetivo prioritario actual."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        content = f"# Προτεραιότητα (Prioridad Actual)\n\n**Objetivo**: {new_goal}\n\n---\n*Actualizado por: {agent} en {timestamp}*\n"
        
        with open(self.goal_path, "w") as f:
            f.write(content)
        self.log_event(agent, "GOAL_UPDATE", f"Nuevo objetivo: {new_goal}")

if __name__ == "__main__":
    # Test simple
    syncer = NexusSync()
    print("Nexus Syncer inicializado.")
