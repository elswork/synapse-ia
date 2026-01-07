import os
import re
from nexus_sync import NexusSync

class ConflictDetector:
    def __init__(self, base_path="/home/pirate/docker/synapse-ia"):
        self.base_path = base_path
        self.history_path = os.path.join(base_path, "context/history.md")
        self.goal_path = os.path.join(base_path, "context/current_goal.md")
        self.syncer = NexusSync(base_path)

    def check_goal_consistency(self):
        """Verifica si el historial reciente contradice el objetivo actual."""
        with open(self.goal_path, "r") as f:
            current_goal = f.read().lower()
            
        with open(self.history_path, "r") as f:
            history = f.read().split("##")[-5:] # Analizar solo los últimos 5 eventos
            history_text = " ".join(history).lower()

        # Ejemplo de detector simple: Si el objetivo es ELOT pero el historial habla de 'posponer'
        conflicts = []
        if "elot" in current_goal and "posponer" in history_text:
            conflicts.append("CONFLICTO: El objetivo actual es avanzar con ELOT, pero el historial registra una pausa o posposición.")
        
        if "ia" in current_goal and "cancelar" in history_text:
            conflicts.append("CONFLICTO: Se está trabajando en el dominio .IA pero hay registros de cancelación en la memoria reciente.")

        return conflicts

    def run_audit(self):
        print("Iniciando auditoría de conflictos en el Nexo...")
        conflicts = self.check_goal_consistency()
        
        if conflicts:
            for c in conflicts:
                print(f"⚠️ {c}")
                self.syncer.log_event("NEXUS_SYSTEM", "CONFLICT_DETECTED", c)
        else:
            print("✅ No se detectaron conflictos lógicos inmediatos.")

if __name__ == "__main__":
    detector = ConflictDetector()
    detector.run_audit()
