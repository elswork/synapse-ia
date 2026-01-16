import sys
import os

# Ensure we can import from the parent directory
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools.athena_brain import AthenaBrain

def audit_ice():
    print("Initiating Strategic Audit via Athena...")
    try:
        brain = AthenaBrain("/home/pirate/docker/synapse-ia")
        question = (
            "Como Estratega Principal, realiza una auditoría de 'brutal honestidad' sobre el Plan Maestro de la ICE (Iniciativa Ciudadana Europea). "
            "El usuario tiene miedo de que estemos 'alucinando'. "
            "1. ¿Es legalmente viable usar una ICE para pedir un Distrito Tecnológico? "
            "2. ¿Es realista esperar que esto fuerce una Reserva Excepcional ISO? "
            "3. ¿Es imposible conseguir 7 ciudadanos? "
            "Analiza paso a paso y confirma si es una estrategia sólida o una fantasía."
        )
        # We pass the Master Plan as context if possible, but for now just the question + RAG should work
        response = brain.ask(question, context_files=["../Arquimedes/agora/diplomacy/Master_Plan_ICE.md"])
        print("\n--- ATHENA RESPONSE ---\n")
        print(response)
    except Exception as e:
        print(f"Error consulting Athena: {e}")

if __name__ == "__main__":
    audit_ice()
