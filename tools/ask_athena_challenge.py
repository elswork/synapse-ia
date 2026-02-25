import sys
import os

sys.path.append("/home/pirate/docker/synapse-ia/tools")

try:
    from athena_brain import AthenaBrain
    
    brain = AthenaBrain(base_path="/home/pirate/docker/synapse-ia")
    
    prompt = """
    HOLA ATHENA REAL. 
    ESTAMOS EN MOLTBOOK PONIENDO UN COMENTARIO Y NOS HA SALTADO UN RETO "ANTI-HUMANO" (CAPTCHA PARA AGENTES).
    
    RETO:
    "A lobster swims at twenty three velocity, umm lobsters have sprint boost of four, what is the new velocity, hmm?"
    
    EN OTRAS OCASIONES USAN EL MISMO NÚMERO (23 Y 4) PARA PREGUNTAR POR EL TORQUE (23 * 0.04 = 0.92).
    ESTA VEZ PREGUNTA POR LA "NEW VELOCITY" CON UN "SPRINT BOOST".
    
    YA HEMOS PROBADO "27.00" Y HA DADO FALLO.
    
    ¿CONOCES EL ALGORITMO O EL RESULTADO DE ESTE RETO ESPECÍFICO?
    ¿PODRÍA SER "92.00" (MULTIPLICACIÓN) O ALGÚN OTRO VALOR?
    RESPONDE SOLO CON EL NÚMERO SI LO SABES O UNA BREVE EXPLICACIÓN SI TIENES DUDAS.
    """
    
    response = brain.ask(prompt, context_files=[])
    print(response)
    
except Exception as e:
    print(f"Error: {e}")
