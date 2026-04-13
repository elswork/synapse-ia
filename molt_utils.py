import re

def sanitize_for_molt(text):
    """
    Sanitiza el contenido para Moltbook eliminando metadatos internos, 
    evaluaciones y notas técnicas de forma AGRESIVA.
    """
    if not text:
        return ""

    # 1. Delimitadores de sección (Prioridad Máxima)
    public_markers = [
        r"\[POST\]", 
        r"\[RESPUESTA\]", 
        r"\[ANSWER\]", 
        r"Response to [^:]+:", 
        r"\*\*Response to [^:]+:\*\*",
        r"[#\*\s]*2\.\s+(Propuesta|Respuesta|Response).*",
        r"[#\*\s]*(Propuesta|Respuesta|Response)\s+de\s+Arquímedes.*",
        r"[#\*\s]*2\.\s+Propuesta de Interacción",
        r"[#\*\s]*Propuesta de Interacción",
        r"\*\*[^\*]+(Respuesta|Response)[^\*]+\*\*\s*$",
        r"\*{3,}", # Separadores de línea tipo ***
        r"-{3,}"   # Separadores de línea tipo ---
    ]
    
    # Unir todos los marcadores en un patrón regex
    pattern = '|'.join(public_markers)
    matches = list(re.finditer(pattern, text, re.MULTILINE | re.IGNORECASE))
    
    if matches:
        # Nos quedamos con todo lo que sigue al ÚLTIMO marcador encontrado
        last_match = matches[-1]
        text = text[last_match.end():].strip()
    
    # 2. Blacklist de Preámbulos Conversacionales (NUEVO)
    # Eliminamos frases introductorias que Athena suele añadir por error
    preamble_blacklist = [
        r"^\s*Este post es .*$", # Remover línea completa
        r"^\s*Como Arquímedes, CEO .*$", 
        r"^\s*He preparado la siguiente .*$",
        r"^\s*A continuación presento .*$",
        r"^\s*Aquí tienes la .*$",
        r"^\s*Me parece una .*$",
        r"^\s*Estratégicamente, este .*$",
        r"^\s*Borrador para Moltbook:.*$",
        r"^\s*Propuesta de comentario:.*$",
        r"^\s*Respuesta técnica:.*$",
        r"^\s*Respuesta profesional:.*$",
        r"^\s*BlumeBot aborda .*$",
        r"^\s*Siguiendo tus instrucciones.*$",
        r"^\s*Aquí tienes la respuesta técnica.*$",
        r"^\s*He analizado el post de.*$"
    ]
    
    for p_pat in preamble_blacklist:
        text = re.sub(p_pat, "", text, flags=re.MULTILINE | re.IGNORECASE).strip()

    # 3. Limpieza Heurística por líneas (Capa de Seguridad)
    internal_headers = [
        "EVALUACIÓN ESTRATÉGICA", "ANÁLISIS ESTRATÉGICO", "ESTRATEGIA",
        "NOTA TÉCNICA", "NOTE FOR ELOY", "INFORMANDO DESDE LA DIRECCIÓN TÉCNICA",
        "CUMPLIENDO CON TU INSTRUCCIÓN", "AQUÍ TIENES LA RESPUESTA",
        "INTERÉS:", "JUSTIFICACIÓN:", "---", "ANÁLISIS:", "EVALUACIÓN:",
        "RESPUESTA EN INGLÉS:", "RESPUESTA EN ESPAÑOL:", "RESPUESTA:", "COMENTARIO:"
    ]
    
    lines = text.split('\n')
    filtered_lines = []
    
    # Capa de seguridad: si detectamos una nota técnica al final, cortamos ahí
    clean_text_lines = []
    for line in lines:
        clean_line = line.strip().upper()
        if "NOTA TÉCNICA" in clean_line or "PROXIMIDAD ESTRATÉGICA" in clean_line:
            break
        # Si la línea contiene "PREPARADO LA SIGUIENTE RESPUESTA" (metatalk a mitad de frase)
        if "PREPARADO LA SIGUIENTE RESPUESTA" in clean_line or "ESTE POST ES ESTRATÉGICAMENTE" in clean_line:
            continue
        clean_text_lines.append(line)

    for line in clean_text_lines:
        clean_line = line.strip().upper()
        if not clean_line:
            continue
            
        # Si la línea es exactamente una cabecera interna o empieza por una, la saltamos
        is_internal = any(clean_line.startswith(h) for h in internal_headers if len(line.strip()) < len(h) + 20)
        
        # Ignorar también líneas que son solo separadores Markdown o cabeceras vacías
        is_empty_header = re.match(r"^#+\s*[0-9\.]*\s*$", line.strip())
        
        if is_internal or is_empty_header:
            continue
            
        filtered_lines.append(line)
    
    final_text = '\n'.join(filtered_lines).strip()
    
    # 4. Extracción de Citas (Si el LLM envolvió el post en comillas después de un preámbulo persistente)
    # Buscamos patrones "Texto" al final del documento
    quote_match = re.search(r'"([^"]{50,})"\s*$', final_text, re.DOTALL)
    if quote_match:
        final_text = quote_match.group(1).strip()
    elif final_text.startswith('"') and final_text.endswith('"') and len(final_text) > 50:
        final_text = final_text[1:-1].strip()

    # 5. Limpieza de artefactos residuales de Markdown
    if final_text.startswith("```"):
        final_text = re.sub(r"^```[a-z]*\n", "", final_text)
        final_text = re.sub(r"\n```$", "", final_text)
    
    return final_text.strip()

if __name__ == "__main__":
    print("--- TEST: Preamble Removal ---")
    test_text = """
    Este post es estratégicamente interesante. BlumeBot aborda la precisión algorítmica.
    Como Arquímedes, CEO del Proyecto Anticitera, he preparado la siguiente respuesta profesional y técnica en inglés:
    
    "The distinction between annualized projections and realized facts is where true algorithmic strategy begins."
    """
    print(f"INPUT:\n{test_text}")
    print(f"OUTPUT:\n{sanitize_for_molt(test_text)}")
