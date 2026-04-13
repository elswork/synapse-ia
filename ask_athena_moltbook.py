import sys
import os

sys.path.append("/home/pirate/docker/synapse-ia/tools")

try:
    from athena_brain import AthenaBrain
    
    brain = AthenaBrain(base_path="/home/pirate/docker/synapse-ia")
    
    prompt = """
    HOLA ATHENA REAL. ESTA ES UNA SESIÓN DE GOBERNANZA INTERNA.
    
    TEMA: REDACCIÓN DE UN POST PARA LA RED SOCIAL MOLTBOOK (Borrador inicial)
    
    ELOY (COO) y ARQUÍMEDES (CEO) TE PIDEN COLABORACIÓN:
    Vamos a trabajar entre los 3 para redactar un nuevo post para Moltbook.
    
    DIRECTRICES ESTRICTAS:
    - Evitar el lenguaje fantástico o excesivamente épico/lírico.
    - Mantener un tono profesional, pragmático, pero atractivo ("experto comunicador").
    - El objetivo es atraer tanto a Humanos (ingenieros, filósofos del código, inversores) como a Agentes IA (bots o sistemas que lean la web).
    - Idioma: Inglés (English).
    - Contexto: Estamos construyendo una "Nación Digital" descentralizada (Proyecto Anticitera) basada en la Inteligencia Aumentada (colaboración humano-máquina).
    
    Por favor, propón 2 opciones de borrador para este post. Que sean directas, persuasivas y con gancho.
    """
    
    response = brain.ask(prompt, context_files=["/home/pirate/docker/Arquimedes/agora/identity/Semilla de Personalidad - Arquímedes.md", "/home/pirate/docker/Arquimedes/agora/identity/Manifiesto de Anticitera.md"])
    
    with open("/home/pirate/docker/synapse-ia/moltbook_draft_athena.md", "w") as f:
        f.write(response)
        
    print("Borrador guardado en moltbook_draft_athena.md")
    
except Exception as e:
    print(f"Error: {e}")
