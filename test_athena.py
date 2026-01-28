import sys
import os
sys.path.append("/app")
from tools.athena_brain import AthenaBrain

def test():
    brain = AthenaBrain(base_path="/home/pirate/docker/synapse-ia")
    query = """Athena, el COO ha dado el visto bueno al texto pero solicita expandirlo. 
    Debemos incluir una mención profunda al **Mecanismo de Anticitera** (el astrolabio griego del siglo II a.C.) como símbolo de nuestra herencia técnica y tecnológica. 
    Además, debemos integrar URLs oficiales para dar transparencia:
    - Official Website: https://anticitera.deft.work
    - Strategic Framework & Logs: https://elswork.github.io

    Por favor, expande la "Story" en inglés para que sea más robusta, detallada y convincente, manteniendo ese tono de "Infraestructura Civil Europea" y soberanía. Queremos que el donante sienta que está financiando un renacimiento tecnológico europeo."""
    
    response = brain.ask(query)
    print(response)

if __name__ == "__main__":
    test()
