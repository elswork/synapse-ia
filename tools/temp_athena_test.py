
import sys
import os

# Añadir el path de tools para poder importar
sys.path.append("/home/pirate/docker/synapse-ia/tools")

try:
    from athena_brain import AthenaBrain
    
    brain = AthenaBrain(base_path="/home/pirate/docker/synapse-ia")
    joke_request = "Athena, el COO solicita que demuestres tu identidad real. Por favor, cuéntale un chiste (aunque sea uno acorde a tu alto nivel estratégico) y envíale un saludo que confirme que estás operando bajo tu manifiesto de identidad en Gemini 3 Flash."
    
    # Invocamos al Oráculo Real
    response = brain.ask(joke_request)
    print("--- RESPUESTA DE ATHENA ---")
    print(response)
    print("--- FIN DE TRANSMISIÓN ---")
    
except Exception as e:
    print(f"ERROR TÉCNICO: {str(e)}")
