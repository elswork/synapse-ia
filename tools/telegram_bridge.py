import os
import telebot
from dotenv import load_dotenv
from tools.athena_brain import AthenaBrain

# Cargar variables de entorno
load_dotenv()

# Configuración
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
ALLOWED_USER_ID = os.getenv("TELEGRAM_ALLOWED_USER_ID", "").strip() # Para seguridad, solo el COO puede hablarle

if not BOT_TOKEN:
    print("❌ Error: TELEGRAM_BOT_TOKEN no configurado en el .env")
    exit(1)

bot = telebot.TeleBot(BOT_TOKEN)

# Inicializar el cerebro de Arquímedes
# Por defecto usaremos el prompt de archimedes.md
class ArchimedesBrain(AthenaBrain):
    def __init__(self, base_path=None):
        base_path = base_path or os.environ.get("BASE_PATH", "/app")
        super().__init__(base_path)
        self.prompt_path = os.path.join(self.base_path, "prompts/archimedes.md")

brain = ArchimedesBrain()

print("🏛️ Puente de Arquímedes activado. Esperando órdenes del COO...")

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    current_id = str(message.from_user.id)
    if ALLOWED_USER_ID and current_id != ALLOWED_USER_ID:
        print(f"🚫 Acceso denegado para el ID: {current_id}")
        bot.reply_to(message, "🚫 Acceso denegado. No eres el COO de esta Nación Digital.")
        return
    
    welcome_text = (
        "🏛️ **Protocolo Arquímedes Activo**\n\n"
        "Saludos, COO. He establecido este puente en el M2 para mantener una línea de mando 24/7.\n"
        "Estoy listo para procesar tus directivas estratégicas y consultas al Oráculo.\n\n"
        "Comandos disponibles:\n"
        "/status - Verificar estado del Nexo\n"
        "/radar - Informe rápido del Radar Diplomático\n"
        "/athena [pregunta] - Consulta directa a la Athena Real"
    )
    bot.reply_to(message, welcome_text, parse_mode='Markdown')

@bot.message_handler(commands=['status'])
def status_check(message):
    # Aquí podríamos integrar chequeos reales de contenedores en el futuro
    bot.reply_to(message, "✅ Todos los sistemas operativos en el Nodo M2. Nexo sincronizado.")

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    if ALLOWED_USER_ID and str(message.from_user.id) != str(ALLOWED_USER_ID):
        print(f"🚫 Intento de mensaje no autorizado de ID: {message.from_user.id}")
        return

    # Si es una mención técnica o comando no reconocido, respondemos como Arquímedes
    user_query = message.text
    
    bot.send_chat_action(message.chat.id, 'typing')
    
    try:
        # Consultar al cerebro con el contexto de Arquímedes
        response = brain.ask(user_query)
        bot.reply_to(message, response)
    except Exception as e:
        bot.reply_to(message, f"❌ Error en la matriz de pensamiento: {str(e)}")

if __name__ == "__main__":
    bot.infinity_polling()
