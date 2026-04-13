import os
import sys
import json
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Añadir el directorio raíz al path para importar tools
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from tools.athena_brain import AthenaBrain
from tools.email_sender import EmailSender

# Carga de variables de entorno
load_dotenv()
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_ALLOWED_USER_ID = os.environ.get("TELEGRAM_ALLOWED_USER_ID")
GITHUB_TOKEN = os.environ.get("GITHUB_PERSONAL_ACCESS_TOKEN")
ADMIN_EMAIL = os.environ.get("ADMIN_EMAIL")

class DailyRadar:
    def __init__(self):
        self.base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        self.brain = AthenaBrain(base_path=self.base_path)
        self.radar_prompt_path = os.path.join(os.path.dirname(__file__), "../prompts/radar_template.md")
        self.email_sender = EmailSender()

    def search_github(self, queries):
        """Busca repositorios en GitHub basados en las queries proporcionadas."""
        results = []
        headers = {}
        if GITHUB_TOKEN:
            headers['Authorization'] = f'token {GITHUB_TOKEN}'
        
        # Filtrar por repositorios creados en la última semana
        last_week = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
        
        for query in queries:
            print(f"Buscando en GitHub: {query}...")
            url = f"https://api.github.com/search/repositories?q={query}+created:>{last_week}&sort=stars&order=desc"
            try:
                response = requests.get(url, headers=headers)
                if response.status_code == 200:
                    items = response.json().get('items', [])
                    for item in items[:5]: # Solo los 5 más relevantes por query
                        results.append({
                            'name': item['full_name'],
                            'url': item['html_url'],
                            'description': item['description'],
                            'stars': item['stargazers_count'],
                            'language': item['language']
                        })
                else:
                    print(f"Error en búsqueda GitHub ({query}): {response.status_code}")
            except Exception as e:
                print(f"Excepción en búsqueda GitHub ({query}): {e}")
        
        return results

    def generate_report(self, raw_data):
        """Usa a Athena para destilar la información y generar el reporte final."""
        with open(self.radar_prompt_path, 'r') as f:
            template = f.read()
        
        # Formatear la data cruda para Athena
        data_str = json.dumps(raw_data, indent=2)
        
        full_query = f"""
        PROCESA ESTA DATA CRUDA Y GENERA EL RADAR TECNOLÓGICO:
        {data_str}
        
        SIGUE ESTA PLANTILLA:
        {template}
        """
        
        print("Generando reporte con Athena...")
        report = self.brain.ask(full_query, log_to_history=True)
        return report

    def notify_telegram(self, report):
        """Envía el reporte vía Telegram."""
        if not TELEGRAM_BOT_TOKEN or not TELEGRAM_ALLOWED_USER_ID:
            print("Error: No se han configurado las variables de Telegram.")
            return

        print("Enviando reporte a Telegram...")
        import telebot # Importación diferida como en news_sentinel.py
        bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)
        
        # Telegram tiene un límite de 4096 caracteres
        if len(report) > 4000:
            parts = [report[i:i+4000] for i in range(0, len(report), 4000)]
            for part in parts:
                bot.send_message(TELEGRAM_ALLOWED_USER_ID, part, parse_mode='Markdown')
        else:
            bot.send_message(TELEGRAM_ALLOWED_USER_ID, report, parse_mode='Markdown')

    def send_email(self, report):
        """Envía el reporte vía Email."""
        if not ADMIN_EMAIL:
            print("Error: ADMIN_EMAIL no configurado.")
            return False

        subject = f"🚨 RADAR TECNOLÓGICO: {datetime.now().strftime('%Y-%m-%d')}"
        
        # Convertimos mínimamente para HTML
        body_html = f"<html><body style='font-family: monospace; white-space: pre-wrap; background: #f4f4f4; padding: 20px;'><div style='background: white; padding: 20px; border-radius: 8px; border: 1px solid #ddd;'>{report}</div></body></html>"
        body_text = report

        print(f"Enviando reporte a {ADMIN_EMAIL}...")
        return self.email_sender.send_direct_email(ADMIN_EMAIL, subject, body_html, body_text)

    def run(self, test_mode=False):
        print(f"[{datetime.now()}] Iniciando misión Radar Tecnológico...")
        
        queries = [
            "mcp-server",
            "model-context-protocol",
            "ai-agent-skills",
            "agentic-workflow",
            "sovereign-ai"
        ]
        
        raw_repos = self.search_github(queries)
        
        if not raw_repos and not test_mode:
            print("No se han encontrado novedades significativas hoy.")
            return

        report = self.generate_report(raw_repos)
        
        if test_mode:
            print("MODO PRUEBA: Reporte generado con éxito.")
        else:
            self.notify_telegram(report)
        
        # Envío por email (siempre intentamos si hay reporte)
        success = self.send_email(report)
        if success:
            print("Email enviado con éxito.")
        else:
            print("Fallo al enviar el email.")
            
        # Guardar copia local en logs
        log_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../Arquimedes/logs/Radar_Tecnologico"))
        os.makedirs(log_dir, exist_ok=True)
        log_file = os.path.join(log_dir, f"radar_{datetime.now().strftime('%Y%m%d_%H%M')}.md")
        with open(log_file, 'w') as f:
            f.write(report)
        print(f"Copia del radar guardada en: {log_file}")

if __name__ == "__main__":
    test = "--test" in sys.argv
    radar = DailyRadar()
    radar.run(test_mode=test)
