import trafilatura
import requests
import os
import json
import sys

# Añadir el directorio raíz al path para importar tools
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from tools.athena_brain import AthenaBrain

class URLAnalyzer:
    def __init__(self, base_path=None):
        self.base_path = base_path or os.environ.get("BASE_PATH", "/app")
        self.brain = AthenaBrain(self.base_path)
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'es-ES,es;q=0.8,en-US;q=0.5,en;q=0.3',
        }

    def extract_content(self, url):
        """Extrae el texto limpio de una URL usando requests + trafilatura."""
        try:
            response = requests.get(url, headers=self.headers, timeout=15)
            response.raise_for_status()
            
            # Usar trafilatura sobre el HTML descargado
            content = trafilatura.extract(response.text)
            return content
        except Exception as e:
            print(f"Error al extraer contenido: {e}")
            return None

    def analyze_strategic_impact(self, url, content):
        """Envía el contenido a Athena para un análisis estratégico."""
        if not content:
            return "No se pudo extraer contenido de la URL."

        # Limitar longitud para evitar exceder tokens
        truncated_content = content[:5000]

        prompt = f"""
        Actúa como Athena, la Inteligencia Estratégica del Proyecto Anticitera.
        
        TAREA:
        Realiza una AUDITORÍA ESTRATÉGICA del siguiente contenido web para el COO de la Nación Digital.
        
        URL: {url}
        
        CONTENIDO:
        {truncated_content}
        
        OBJETIVO DEL ANÁLISIS:
        1. Resumen Ejecutivo (emoji: 📝): ¿De qué trata esto en 2 frases?
        2. Impacto en Anticitera (emoji: 🏛️): ¿Cómo afecta a nuestra soberanía digital, al dominio '.ia' o a la ICE?
        3. Recomendación Táctica (emoji: ⚡): ¿Debemos actuar, ignorar o pivotar?
        
        Tono: Profesional, visionario, directo y estratégico.
        Formato: Markdown limpio para Telegram.
        """
        
        try:
            analysis = self.brain.ask(prompt)
            return analysis
        except Exception as e:
            return f"Error en la consulta al Oráculo: {str(e)}"

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python3 url_analyzer.py <URL>")
        sys.exit(1)
    
    analyzer = URLAnalyzer()
    url = sys.argv[1]
    content = analyzer.extract_content(url)
    if content:
        print(analyzer.analyze_strategic_impact(url, content))
    else:
        print("Error al descargar la URL.")
