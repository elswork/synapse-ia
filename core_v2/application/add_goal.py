from core_v2.domain.interfaces.sovereign_memory import ISovereignMemory
from core_v2.domain.interfaces.strategic_consultant import IStrategicConsultant
from core_v2.domain.models.goal import Goal, GoalStatus

class AddGoalUseCase:
    def __init__(self, memory: ISovereignMemory, consultant: IStrategicConsultant):
        self.memory = memory
        self.consultant = consultant

    def execute(self, description: str) -> str:
        # 1. IA Analysis
        analysis = self.consultant.ask(f"Analiza esta directiva para el Proyecto Anticitera: {description}")
        
        # 2. Persist (Simplificado para este ejemplo de Core)
        # En una versión completa, se crearía el objeto Goal y se guardaría
        # self.memory.save_goal(...) 
        
        return f"✅ Directiva analizada por el Núcleo:\n{analysis}"
