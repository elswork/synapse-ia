import os
import telebot
from dotenv import load_dotenv
from tools.athena_brain import AthenaBrain
from tools.select_mep_proposal import MEPSelector
from tools.email_sender import EmailSender

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
        "/athena [pregunta] - Consulta directa a la Athena Real\n"
        "/pasar_mep [nombre] - Generar y enviarme una propuesta MEP"
    )
    bot.reply_to(message, welcome_text, parse_mode='Markdown')

@bot.message_handler(commands=['status'])
def status_check(message):
    bot.reply_to(message, "✅ Todos los sistemas operativos en el Nodo M2. Nexo sincronizado.")

@bot.message_handler(commands=['pasar_mep'])
def pasar_mep(message):
    if ALLOWED_USER_ID and str(message.from_user.id) != str(ALLOWED_USER_ID):
        return

    # Extraer nombre si existe
    args = message.text.split(maxsplit=1)
    name_filter = args[1] if len(args) > 1 else None

    bot.send_message(message.chat.id, "🏛️ *Protocolo Arquímedes:* Iniciando selección de candidato y forja de propuesta...", parse_mode='Markdown')
    bot.send_chat_action(message.chat.id, 'typing')

    try:
        selector = MEPSelector()
        proposal = selector.generate_proposal(name_filter)

        if "error" in proposal:
            bot.reply_to(message, f"❌ {proposal['error']}")
            return

        mep = proposal['mep']
        email_data = proposal['email']

        # Cargar template HTML
        template_path = os.path.join(os.path.dirname(__file__), "templates/mep_email_template.html")
        with open(template_path, 'r') as f:
            template_html = f.read()

        # Reemplazar variables en template
        rich_html = template_html.replace("{{mep_name}}", mep['name'])
        rich_html = rich_html.replace("{{mep_country}}", mep['country'])
        rich_html = rich_html.replace("{{mep_email}}", mep['email'])
        rich_html = rich_html.replace("{{subject}}", email_data['subject'])
        rich_html = rich_html.replace("{{body_text}}", email_data['body'])

        # Enviar Email
        sender = EmailSender()
        success = sender.send_mep_email(
            mep['name'], mep['country'], mep['email'],
            email_data['subject'], rich_html, email_data['body']
        )

        if success:
            saved_path = selector.save_proposal(proposal)
            bot.reply_to(message, 
                f"✅ **Propuesta enviada a elswork@gmail.com**\n\n"
                f"**Candidato:** {mep['name']} ({mep['country']})\n"
                f"**Email:** `{mep['email']}`\n\n"
                f"Revisa tu bandeja de entrada. He guardado el borrador en:\n`{saved_path}`",
                parse_mode='Markdown'
            )
        else:
            bot.reply_to(message, "❌ Error al enviar el correo. Revisa los logs del sistema.")

    except Exception as e:
        bot.reply_to(message, f"❌ Error crítico en la forja: {str(e)}")

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
