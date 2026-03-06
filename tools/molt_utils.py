import re

def sanitize_for_molt(text):
    """
    Sanitiza el contenido para Moltbook eliminando metadatos internos, 
    evaluaciones y notas técnicas.
    """
    if not text:
        return ""

    # 1. Delimitadores de sección (Prioridad Máxima)
    # Buscamos el último rastro de etiquetas que indican el inicio de la respuesta pública
    # Usamos re.MULTILINE para asegurar que ^ detecte marcadores al inicio de cualquier línea
    public_markers = [
        r"^\[POST\]", 
        r"^\[RESPUESTA\]", 
        r"^\[ANSWER\]", 
        r"^Response to [^:]+:", 
        r"^\*\*Response to [^:]+:\*\*",
        r"^### 2\. Propuesta de Interacción",
        r"^### Propuesta de Interacción"
    ]
    
    # Unir todos los marcadores en un patrón regex
    pattern = '|'.join(public_markers)
    matches = list(re.finditer(pattern, text, re.MULTILINE | re.IGNORECASE))
    
    if matches:
        # Nos quedamos con todo lo que sigue al ÚLTIMO marcador encontrado
        last_match = matches[-1]
        text = text[last_match.end():].strip()
    
    # 2. Limpieza Heurística por líneas (Capa de Seguridad 2)
    # Eliminamos líneas que suelen ser cabeceras o notas internas
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
        clean_text_lines.append(line)

    for line in clean_text_lines:
        clean_line = line.strip().upper()
        
        # Si la línea es exactamente una cabecera interna o empieza por una, la saltamos
        is_internal = any(clean_line.startswith(h) for h in internal_headers if len(line.strip()) < len(h) + 20)
        
        # Ignorar también líneas que son solo separadores Markdown o cabeceras vacías
        is_empty_header = re.match(r"^#+\s*[0-9\.]*\s*$", line.strip())
        
        if is_internal or is_empty_header:
            continue
            
        filtered_lines.append(line)
    
    final_text = '\n'.join(filtered_lines).strip()
    
    # 3. Limpieza de artefactos residuales de Markdown
    # Eliminar bloques de código envolventes si Athena los puso por error
    if final_text.startswith("```"):
        final_text = re.sub(r"^```[a-z]*\n", "", final_text)
        final_text = re.sub(r"\n```$", "", final_text)
    
    return final_text.strip()

if __name__ == "__main__":
    # Test cases
    test_text = """
    ### 1. Evaluación Estratégica
    Interés: ALTO. Justificación: Bla bla.
    
    ### 2. Propuesta de Interacción (Arquímedes)
    **Response to midos-pengu:**
    Hello world! This is the public part.
    
    Nota Técnica de Arquímedes: No olvides el café.
    """
    print("--- TEST 1 ---")
    print(sanitize_for_molt(test_text))
    
    test_text_2 = "[EVAL] Analysis [POST] Actual comment text"
    print("\n--- TEST 2 ---")
    print(sanitize_for_molt(test_text_2))
