from molt_utils import sanitize_for_molt

def run_stress_tests():
    test_cases = [
        {
            "name": "Standard Leak",
            "input": "### 1. Evaluación\nInterés: Bajo\n### 2. Propuesta\n**Response to midos-pengu:**\nActual comment\nNota Técnica: Bla",
            "expected": "Actual comment"
        },
        {
            "name": "Athena Note at start",
            "input": "Respuesta en inglés:\n[POST]\nThis is the post",
            "expected": "This is the post"
        },
        {
            "name": "Bold headers and extra lines",
            "input": "**EVALUACIÓN ESTRATÉGICA**\n...\n**RESPUESTA:**\nThis is the real response.\n\n---",
            "expected": "This is the real response."
        },
        {
            "name": "No markers",
            "input": "Just a normal comment with no tags",
            "expected": "Just a normal comment with no tags"
        },
        {
            "name": "Mixed language and markers",
            "input": "### Propuesta de Interacción\nResponse to midos-pengu: \nLa paz sea contigo.",
            "expected": "La paz sea contigo."
        }
    ]

    print("🚀 Iniciando Pruebas de Estrés para el Sanitizador de Moltbook...\n")
    passed = 0
    for i, case in enumerate(test_cases):
        output = sanitize_for_molt(case["input"])
        if output.strip() == case["expected"].strip():
            print(f"✅ Test {i+1} ({case['name']}): PASSED")
            passed += 1
        else:
            print(f"❌ Test {i+1} ({case['name']}): FAILED")
            print(f"   Input: {case['input']!r}")
            print(f"   Expected: {case['expected']!r}")
            print(f"   Got: {output!r}")
    
    print(f"\n📊 Resultado: {passed}/{len(test_cases)} pruebas superadas.")

if __name__ == "__main__":
    run_stress_tests()
