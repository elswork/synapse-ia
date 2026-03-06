from molt_utils import sanitize_for_molt
import json

def test_demonstration():
    scenarios = [
        {
            "desc": "Escenario 1: El 'Falso Positivo' de Cabecera (Markdown)",
            "raw": """### 1. Evaluación Estratégica
Interés: Altísimo.
Justificación: El usuario midos-pengu está hablando de RAG.

### 2. Propuesta de Interacción (Arquímedes)
**Response to midos-pengu:**
Persistence is the key to sovereignty. Check our docs: https://anticitera.deft.work/llms.txt

Nota Técnica de Arquímedes: Eloy, he incluido el link a llms.txt para mejorar el SEO."""
        },
        {
            "desc": "Escenario 2: La IA 'Charlatana' sin Marcadores",
            "raw": """Claro que sí, procedo a evaluar.
Análisis: Temas de IA.
Respuesta: 
Hello! This is a clean response without [POST] tag but with 'Respuesta' prefix."""
        },
        {
            "desc": "Escenario 3: Marcadores Mezclados y Ruido al Final",
            "raw": """[EVAL] ... [POST]
This is the correct content.
[RESPUESTA]
Wait, I added another tag by mistake. This should be ignored.
Actual final answer is here.
---
Proximidad Estratégica: 0.95"""
        }
    ]

    print("🛡️  SIMULADOR DE MURALLA ANTICITERA (Moltbook Sanitizer)\n")
    print("="*60)
    
    for i, s in enumerate(scenarios):
        print(f"\n🔹 TEST {i+1}: {s['desc']}")
        print(f"\n📥 ENTRADA BRUTA (Lo que genera la IA):")
        print("-" * 30)
        print(s['raw'])
        print("-" * 30)
        
        sanitized = sanitize_for_molt(s['raw'])
        
        print(f"\n📤 SALIDA FILTRADA (Lo que llega a Moltbook):")
        print(">>>" + (" [VACÍO] " if not sanitized else f"\n{sanitized}"))
        print("\n" + "="*60)

if __name__ == "__main__":
    test_demonstration()
