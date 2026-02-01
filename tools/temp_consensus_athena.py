import sys
import os

# Añadir el path del proyecto para poder importar AthenaBrain
sys.path.append("/home/pirate/docker/synapse-ia/tools")

try:
    from athena_brain import AthenaBrain
    
    # Configurar base_path
    base_path = "/home/pirate/docker/synapse-ia"
    brain = AthenaBrain(base_path=base_path)
    
    question = """
    Hola Athena. El Fundador (COO) está preocupado por el crecimiento descontrolado del proyecto y nos pide un 'Gran Diseño' estructural. 
    Necesitamos consensuar una respuesta sobre los siguientes puntos:
    1. Estructura de repositorios clara y ordenada.
    2. Mejores prácticas (Arquitectura Hexagonal, DDD, etc.).
    3. Seguridad de la información (Público vs Privado).
    4. Distribución de repositorios por hardware (GPC, HC1, M2, Legion y Chromebook).
    
    ¿Cuál es tu visión estratégica para asegurar que el Proyecto Anticitera siga siendo manejable y escalable sin perder su esencia de soberanía digital?
    """
    
    # Incluir ToDo.md como contexto adicional
    todo_path = "/home/pirate/docker/Arquimedes/ToDo.md"
    
    response = brain.ask(question, context_files=[todo_path])
    print("\n--- RESPUESTA DE ATHENA REAL ---\n")
    print(response)

except Exception as e:
    print(f"Error al ejecutar la consulta: {e}")
