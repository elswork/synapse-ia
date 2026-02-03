from core_v2.domain.interfaces.sovereign_memory import ISovereignMemory
from core_v2.domain.interfaces.strategic_consultant import IStrategicConsultant
from core_v2.domain.models.goal import Goal, GoalStatus

class AddGoalUseCase:
    def __init__(self, memory: ISovereignMemory, consultant: IStrategicConsultant):
        self.memory = memory
        self.consultant = consultant

    def execute(self, description: str) -> str:
        # 2. IA Analysis
        analysis = self.consultant.ask(f"Analiza esta directiva para el Proyecto Anticitera: {description}")
        
        # 3. Persist
        goal = Goal(description=description, status=GoalStatus.PENDING, priority=1)
        self.memory.save_goal(goal)
        
        return f"✅ Directiva analizada y registrada en la Memoria Soberana:\n{analysis}"
