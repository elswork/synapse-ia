import os
import json
import time
from datetime import datetime, timedelta
import sys

# Añadir el directorio raíz al path para importar tools
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from tools.email_sender import EmailSender

class MassMailingScheduler:
    def __init__(self, base_path=None):
        self.base_path = base_path or os.environ.get("BASE_PATH", "/app")
        self.state_file = os.path.join(self.base_path, "context/data/mailing_state.json")
        self.queue_file = os.path.join(self.base_path, "context/data/mailing_queue.json")
        self.sender = EmailSender()
        self.load_state()

    def load_state(self):
        if os.path.exists(self.state_file):
            with open(self.state_file, 'r', encoding='utf-8') as f:
                self.state = json.load(f)
        else:
            self.state = {
                "campaign_start_date": datetime.now().strftime("%Y-%m-%d"),
                "emails_sent_today": 0,
                "last_send_date": datetime.now().strftime("%Y-%m-%d"),
                "total_emails_sent": 0
            }

    def save_state(self):
        os.makedirs(os.path.dirname(self.state_file), exist_ok=True)
        with open(self.state_file, 'w', encoding='utf-8') as f:
            json.dump(self.state, f, indent=4)

    def load_queue(self):
        if os.path.exists(self.queue_file):
            with open(self.queue_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []

    def save_queue(self, queue):
        os.makedirs(os.path.dirname(self.queue_file), exist_ok=True)
        with open(self.queue_file, 'w', encoding='utf-8') as f:
            json.dump(queue, f, indent=4)

    def get_daily_limit(self):
        start_date = datetime.strptime(self.state["campaign_start_date"], "%Y-%m-%d")
        today = datetime.now()
        days_active = (today - start_date).days

        # Lógica de IP Warming (Calentamiento Exponencial)
        if days_active < 7:
            return 500      # Semana 1
        elif days_active < 14:
            return 2500     # Semana 2
        elif days_active < 21:
            return 10000    # Semana 3
        elif days_active < 28:
            return 30000    # Semana 4
        else:
            return 150000   # Régimen de Crucero para llegar a 1 Millón

    def run_daily_batch(self):
        if not self.sender.use_ses:
            print("⚠️ ADVERTENCIA: Ejecutando campañas masivas sin Amazon SES (API). Se usará SMTP. Alta probabilidad de bloqueo.")
            
        today_str = datetime.now().strftime("%Y-%m-%d")
        
        # Reset daily counter if it's a new day
        if self.state["last_send_date"] != today_str:
            self.state["emails_sent_today"] = 0
            self.state["last_send_date"] = today_str
            self.save_state()

        limit = self.get_daily_limit()
        available_quota = limit - self.state["emails_sent_today"]

        if available_quota <= 0:
            print(f"🛑 Límite de calentamiento IP alcanzado por hoy ({limit} correos). Abortando batch.")
            return

        queue = self.load_queue()
        if not queue:
            print("📭 La cola de envíos masivos está vacía.")
            return

        print(f"🚀 Iniciando Batch Masivo. Límite diario: {limit}. Cuota restante: {available_quota}.")
        
        sent_count = 0
        emails_to_send = queue[:available_quota]
        remaining_queue = queue[available_quota:]

        for task in emails_to_send:
            recipient = task.get("recipient")
            subject = task.get("subject")
            body_html = task.get("body_html")
            body_text = task.get("body_text")

            print(f"Enviando correo a {recipient}...")
            success = self.sender.send_direct_email(recipient, subject, body_html, body_text)
            
            if success:
                sent_count += 1
                self.state["emails_sent_today"] += 1
                self.state["total_emails_sent"] += 1
            else:
                # Si falla, podemos reinyectarlo en la cola si es un soft bounce, 
                # pero para este MVP lo descartamos o lo registramos en logs.
                print(f"❌ Error al enviar a {recipient}")

            # Pequeño delay para no saturar la API o SMTP de golpe
            time.sleep(0.5)

        self.save_state()
        self.save_queue(remaining_queue)
        print(f"✅ Batch completado. Enviados: {sent_count}. Total de la campaña: {self.state['total_emails_sent']}.")

if __name__ == "__main__":
    scheduler = MassMailingScheduler()
    scheduler.run_daily_batch()
