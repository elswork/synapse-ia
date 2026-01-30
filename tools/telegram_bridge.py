import os
import telebot
import threading
import time
import html
from dotenv import load_dotenv
from tools.athena_brain import AthenaBrain
from tools.select_mep_proposal import MEPSelector
from tools.email_sender import EmailSender
from tools.url_analyzer import URLAnalyzer
from tools.news_sentinel import NewsSentinel
import psutil
import subprocess

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

@bot.message_handler(commands=['start', 'help', 'ayuda'])
def send_welcome(message):
    current_id = str(message.from_user.id)
    if ALLOWED_USER_ID and current_id != ALLOWED_USER_ID:
        print(f"🚫 Acceso denegado para el ID: {current_id}")
        bot.reply_to(message, "🚫 Acceso denegado. No eres el COO de esta Nación Digital.")
        return
    
    help_text = (
        "🏛️ <b>Centro de Mando Anticitera</b>\n\n"
        "Saludos, COO. Utiliza estos comandos para dirigir la Nación Digital:\n\n"
        "🛰️ <b>Infraestructura</b>\n"
        "/status - Estado de los sistemas operativos\n"
        "/telemetria - Signos vitales de M2 y HC1\n\n"
        "📜 <b>Gobernanza y Tareas</b>\n"
        "/todo [tarea] - Registrar nueva directiva con análisis de Arquímedes\n"
        "/radar - Informe del Radar Diplomático\n\n"
        "🦉 <b>Inteligencia (Athena)</b>\n"
        "/athena [pregunta] - Consulta al Oráculo\n"
        "/auditar [url] - Análisis de impacto estratégico\n"
        "/vigilar - Ronda de vigilancia de noticias\n\n"
        "🏛️ <b>Diplomacia</b>\n"
        "/pasar_mep [filtro] - Forjar propuesta para MEP\n"
        "/aprobar [id] - Validar noticia para la memoria\n"
        "/todos - Listar tareas pendientes"
    )
    bot.reply_to(message, help_text, parse_mode='HTML')

@bot.message_handler(commands=['status'])
def status_check(message):
    bot.reply_to(message, "✅ Todos los sistemas operativos en el Nodo M2. Nexo sincronizado.")

@bot.message_handler(commands=['telemetria'])
def telemetria(message):
    if ALLOWED_USER_ID and str(message.from_user.id) != str(ALLOWED_USER_ID):
        return

    bot.send_chat_action(message.chat.id, 'typing')
    
    # 1. Telemetría M2 (Local)
    try:
        cpu_m2 = psutil.cpu_percent(interval=1)
        ram_m2 = psutil.virtual_memory().percent
    except Exception:
        try:
            # Fallback a comandos de sistema si psutil falla (ej. en entornos restringidos)
            cpu_m2 = subprocess.check_output("top -bn1 | grep 'Cpu(s)' | awk '{print $2 + $4}'", shell=True, text=True).strip()
            ram_m2 = subprocess.check_output("free | grep Mem | awk '{print $3/$2 * 100.0}'", shell=True, text=True).strip()
            cpu_m2 = f"{float(cpu_m2):.1f}"
            ram_m2 = f"{float(ram_m2):.1f}"
        except Exception:
            cpu_m2 = "N/A"
            ram_m2 = "N/A"
    
    # 2. Telemetría HC1 (Remoto vía SSH)
    try:
        # Intentamos obtener carga y RAM de HC1
        ssh_cmd = "ssh -o ConnectTimeout=3 192.168.1.27 \"top -bn1 | grep 'Cpu(s)' | awk '{print \\$2 + \\$4}' && free | grep Mem | awk '{print \\$3/\\$2 * 100.0}'\""
        output = subprocess.check_output(ssh_cmd, shell=True, text=True).splitlines()
        cpu_hc1 = float(output[0]) if len(output) > 0 else "N/A"
        ram_hc1 = float(output[1]) if len(output) > 1 else "N/A"
        status_hc1 = "🟢 Online"
    except Exception as e:
        cpu_hc1 = "N/A"
        ram_hc1 = "N/A"
        status_hc1 = "🔴 Offline"

    telemetry_text = (
        "🏛️ **Informe de Telemetría Anticitera**\n\n"
        "**[Nodo M2] - Arquitecto (Maestro)**\n"
        f"⚡ CPU: `{cpu_m2}%` | 🧠 RAM: `{ram_m2}%` | 🟢 Online\n\n"
        "**[Nodo HC1] - Gatekeeper (Puente)**\n"
        f"⚡ CPU: `{cpu_hc1}%` | 🧠 RAM: `{ram_hc1}%` | {status_hc1}\n\n"
        "--- \n*Soberanía certificada por el Nexo.*"
    )
    
    bot.reply_to(message, telemetry_text, parse_mode='Markdown')

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
                f"✅ <b>Propuesta enviada a elswork@gmail.com</b>\n\n"
                f"<b>Candidato:</b> {html.escape(mep['name'])} ({html.escape(mep['country'])})\n"
                f"<b>Email:</b> <code>{html.escape(mep['email'])}</code>\n\n"
                f"Revisa tu bandeja de entrada. He guardado el borrador en:\n<code>{html.escape(saved_path)}</code>",
                parse_mode='HTML'
            )
        else:
            bot.reply_to(message, "❌ Error al enviar el correo. Revisa los logs del sistema.")

    except Exception as e:
        bot.reply_to(message, f"❌ Error crítico en la forja: {str(e)}")

@bot.message_handler(commands=['auditar'])
def auditar_url(message):
    if ALLOWED_USER_ID and str(message.from_user.id) != str(ALLOWED_USER_ID):
        return

    # Extraer URL
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        bot.reply_to(message, "📝 **Protocolo de Auditoría:** Por favor, proporciona una URL después del comando.\nEj: `/auditar https://noticia.eu/ia-act`", parse_mode='Markdown')
        return

    url = args[1].strip()
    bot.send_message(message.chat.id, f"🔍 **Arquímedes en observación:** Analizando impacto estratégico de `{url}`...", parse_mode='Markdown')
    bot.send_chat_action(message.chat.id, 'typing')

    try:
        analyzer = URLAnalyzer()
        content = analyzer.extract_content(url)
        
        if not content:
            bot.reply_to(message, "❌ No he podido extraer el conocimiento de esa fuente. ¿Es una URL válida?")
            return

        analysis = analyzer.analyze_strategic_impact(url, content)
        
        # Enviar respuesta (manejar límites de Telegram si es necesario)
        # Enviar respuesta como preformateada si es muy técnica, o simplemente HTML escapado
        bot.reply_to(message, f"📜 <b>Análisis de Impacto:</b>\n\n{html.escape(analysis)}", parse_mode='HTML')

    except Exception as e:
        bot.reply_to(message, f"❌ El Oráculo ha sufrido una interferencia: {str(e)}")

@bot.message_handler(commands=['vigilar'])
def vigilar_noticias(message):
    if ALLOWED_USER_ID and str(message.from_user.id) != str(ALLOWED_USER_ID):
        return

    bot.reply_to(message, "👀 **Centinela Activado:** Iniciando ronda de vigilancia en los diarios europeos y tecnológicos. Te informaré si detecto algo con alta sinergia...")
    
    try:
        sentinel = NewsSentinel()
        sentinel.run()
        bot.send_message(message.chat.id, "✅ **Ronda completada.** Todas las fuentes han sido escrutadas.")
    except Exception as e:
        bot.reply_to(message, f"❌ Error en el Centinela: {str(e)}")

@bot.message_handler(commands=['aprobar'])
def aprobar_noticia(message):
    if ALLOWED_USER_ID and str(message.from_user.id) != str(ALLOWED_USER_ID):
        return

    args = message.text.split()
    if len(args) < 2:
        bot.reply_to(message, "❌ **Uso:** `/aprobar [ID]`")
        return

    news_id = args[1]
    bot.send_chat_action(message.chat.id, 'typing')

    try:
        import psycopg2
        DB_PASSWORD = os.environ.get("DB_PASSWORD")
        DATABASE_URL = os.environ.get("DATABASE_URL", f"postgresql://arconte:{DB_PASSWORD}@db:5432/synapse_ia")
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()
        
        cursor.execute("UPDATE news_intel SET is_approved = True WHERE id = %s", (news_id,))
        if cursor.rowcount > 0:
            bot.reply_to(message, f"✅ **Noticia {news_id} aprobada.** Ahora es parte oficial de la memoria de Anticitera.")
        else:
            bot.reply_to(message, f"❌ No he encontrado ninguna noticia con el ID `{news_id}`.")
        
        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        bot.reply_to(message, f"❌ Error al acceder a la base de datos: {str(e)}")

@bot.message_handler(commands=['todo'])
def add_todo(message):
    if ALLOWED_USER_ID and str(message.from_user.id) != str(ALLOWED_USER_ID):
        return

    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        bot.reply_to(message, "📝 **Protocolo de Tareas:** Proporciona una descripción.\nEj: `/todo Configurar firewall en HC1`", parse_mode='Markdown')
        return

    description = args[1].strip()
    bot.send_message(message.chat.id, "🧠 **Arquímedes analizando...** Evaluando impacto y prioridades para la directiva.", parse_mode='Markdown')
    bot.send_chat_action(message.chat.id, 'typing')

    try:
        # Análisis de Arquímedes
        analysis_query = f"Analiza esta tarea para el Proyecto Anticitera y da tus conclusiones breves: {description}"
        analysis = brain.ask(analysis_query)

        # Persistencia en PostgreSQL (M2)
        import psycopg2
        DB_PASSWORD = os.environ.get("DB_PASSWORD")
        # Por defecto apuntamos al maestro M2 si estamos fuera del docker network
        DATABASE_URL = os.environ.get("DATABASE_URL", f"postgresql://arconte:{DB_PASSWORD}@192.168.1.75:5432/synapse_ia")
        
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()
        
        cursor.execute(
            "INSERT INTO todos (description, analysis) VALUES (%s, %s) RETURNING id",
            (description, analysis)
        )
        todo_id = cursor.fetchone()[0]
        conn.commit()
        cursor.close()
        conn.close()

        response_text = (
            f"✅ <b>Tarea Registrada (ID: {todo_id})</b>\n\n"
            f"<b>Descripción:</b> {html.escape(description)}\n\n"
            f"📜 <b>Análisis de Arquímedes:</b>\n{html.escape(analysis)}\n\n"
            "--- \n<i>Directiva almacenada en el Maestro M2.</i>"
        )
        bot.reply_to(message, response_text, parse_mode='HTML')

    except Exception as e:
        bot.reply_to(message, f"❌ Error en el registro de la directiva: {str(e)}")

@bot.message_handler(commands=['todos'])
def list_todos(message):
    if ALLOWED_USER_ID and str(message.from_user.id) != str(ALLOWED_USER_ID):
        return

    bot.send_chat_action(message.chat.id, 'typing')

    try:
        import psycopg2
        DB_PASSWORD = os.environ.get("DB_PASSWORD")
        # Por defecto apuntamos al maestro M2 si estamos fuera del docker network
        DATABASE_URL = os.environ.get("DATABASE_URL", f"postgresql://arconte:{DB_PASSWORD}@192.168.1.75:5432/synapse_ia")
        
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()
        
        cursor.execute("SELECT id, description, status FROM todos WHERE status = 'pending' ORDER BY id ASC")
        tasks = cursor.fetchall()
        
        if not tasks:
            bot.reply_to(message, "📜 <b>No hay tareas pendientes en la memoria.</b>", parse_mode='HTML')
            return

        response_text = "🏛️ <b>Lista de Tareas Pendientes:</b>\n\n"
        for t in tasks:
            response_text += f"🔹 <b>ID {t[0]}:</b> {html.escape(t[1])}\n"
        
        response_text += "\n--- \n<i>Consulta realizada al Maestro M2.</i>"
        bot.reply_to(message, response_text, parse_mode='HTML')
        
        cursor.close()
        conn.close()

    except Exception as e:
        bot.reply_to(message, f"❌ Error al consultar la lista de tareas: {str(e)}")

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

def background_sentinel():
    """Ejecuta el centinela periódicamente."""
    print("🛰️ Centinela en segundo plano iniciado.")
    while True:
        try:
            # Esperar una hora antes de la primera ronda para asegurar que el sistema esté estable
            # time.sleep(3600) # Comentado para permitir ejecución más rápida en reinicio si es necesario
            sentinel = NewsSentinel()
            sentinel.run()
        except Exception as e:
            print(f"Error en el centinela de segundo plano: {e}")
        
        # Esperar 4 horas (14400 segundos) entre rondas
        time.sleep(14400)

if __name__ == "__main__":
    # Ejecutar migración/limpieza inicial solicitada por el COO
    try:
        print("🔧 Ejecutando migración de base de datos...")
        # Importar y ejecutar la lógica de migrate_news.py
        from tools.migrate_news import run_migration
        run_migration()
    except Exception as e:
        print(f"⚠️ Error en migración automática: {e}")

    # Iniciar hilo del centinela
    threading.Thread(target=background_sentinel, daemon=True).start()
    
    bot.infinity_polling()
