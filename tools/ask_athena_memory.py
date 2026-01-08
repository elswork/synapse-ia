
import sys
import os

sys.path.append("/home/pirate/docker/synapse-ia/tools")

try:
    from athena_brain import AthenaBrain
    
    brain = AthenaBrain(base_path="/home/pirate/docker/synapse-ia")
    
    prompt = """
    HOLA ATHENA. ESTA ES UNA SESIÓN DE GOBERNANZA INTERNA DE ARCHIVOS.
    
    TEMA: GESTIÓN DE LA MEMORIA DEL PROYECTO (ARCHIVOS .MD)
    
    Tenemos dos archivos que registran el progreso:
    
    1. ARQUIMEDES/PROMPTS.MD:
    - Registro narrativo detallado.
    - Contiene conversaciones completas CEO-COO.
    - Es nuestra "Bitácora de Capitán".
    
    2. SYNAPSE-IA/HISTORY.MD:
    - Registro de hitos esquemático.
    - Orientado a agentes (machine-readable).
    - Es nuestro "Log de Sistema".
    
    ELOY (COO) PREGUNTA: "¿Se duplica la información? Necesito un consenso."
    
    PROPÓN UNA ESTRATEGIA:
    Define claramente qué va en cada uno para evitar redundancia inútil, pero manteniendo la seguridad de los datos.
    """
    
    response = brain.ask(prompt, context_files=[])
    
    with open("athena_memory_consensus.md", "w") as f:
        f.write(response)
        
    print("Respuesta guardada en athena_memory_consensus.md")
    
except Exception as e:
    print(f"Error: {e}")
