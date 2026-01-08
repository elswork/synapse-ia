from athena_brain import AthenaBrain
import sys

brain = AthenaBrain()
pregunta = "Athena, el COO reporta que elswork.anticitera no resuelve en navegadores Web3 (Puma/Beacon). ¿Qué implicaciones estratégicas tiene que nuestra capital digital sea inaccesible? ¿Cómo afecta esto a nuestra credibilidad ante ELOT?"
print(brain.ask(pregunta, context_files=['context/current_goal.md', 'context/history.md']))

from tools.athena_brain import AthenaBrain

def test_rag():
    athena = AthenaBrain()
    print("Probando Athena con Memoria RAG...")
    respuesta = athena.ask("¿Cuál es el objetivo prioritario actual y qué se decidió sobre Docker?")
    print("-" * 30)
    print(f"Respuesta de Athena:\n{respuesta}")

if __name__ == "__main__":
    test_rag()
