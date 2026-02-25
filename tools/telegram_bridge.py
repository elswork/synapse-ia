import os
import telebot
import threading
import time
import html
from dotenv import load_dotenv
from tools.athena_brain import AthenaBrain
from tools.select_mep_proposal import MEPSelector
from tools.select_bunny_proposal import BunnySelector
from tools.moltbook_heartbeat import execute_heartbeat
from tools.email_sender import EmailSender
from tools.url_analyzer import URLAnalyzer
from tools.news_sentinel import NewsSentinel
import psutil
import subprocess
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import threading
import schedule

# Cargar variables de entorno
load_dotenv()

# Configuración
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
ALLOWED_USER_ID = os.getenv("TELEGRAM_ALLOWED_USER_ID", "").strip() # Para seguridad, solo el COO puede hablarle

# Global cache for pending bunny proposals
pending_bunny_proposals = {}
TEST_BUNNY_MODE = False

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
        "/pasar_bunny [filtro] - Forjar propuesta para Arconte Experto\n"
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

@bot.message_handler(commands=['pasar_bunny'])
def pasar_bunny(message):
    if ALLOWED_USER_ID and str(message.from_user.id) != str(ALLOWED_USER_ID):
        return

    # Extraer nombre si existe
    args = message.text.split(maxsplit=1)
    name_filter = args[1] if len(args) > 1 else None

    bot.send_message(message.chat.id, "🏛️ *Protocolo Arquímedes (Operación Bad Bunny):* Iniciando selección de Arconte y forja de invitación...", parse_mode='Markdown')
    bot.send_chat_action(message.chat.id, 'typing')

    try:
        selector = BunnySelector()
        proposal = selector.generate_proposal(name_filter)

        if "error" in proposal:
            bot.send_message(message.chat.id, f"❌ {proposal['error']}")
            return

        expert = proposal['expert']
        email_data = proposal['email']

        # Cargar template HTML
        template_path = os.path.join(os.path.dirname(__file__), "templates/bunny_email_template.html")
        with open(template_path, 'r', encoding='utf-8') as f:
            template_html = f.read()

        # Reemplazar variables en template
        rich_html = template_html.replace("{{expert_name}}", expert['name'])
        rich_html = rich_html.replace("{{expert_country}}", expert['country'])
        rich_html = rich_html.replace("{{expert_role}}", expert['role'])
        rich_html = rich_html.replace("{{expert_email}}", expert['email'])
        rich_html = rich_html.replace("{{subject}}", email_data['subject_local'])
        rich_html = rich_html.replace("{{body_text}}", email_data['body_local'])
        rich_html = rich_html.replace("{{body_spanish}}", email_data['body_spanish'])

        import time
        # Guardar en la caché de pendientes
        proposal_id = f"bunny_{int(time.time())}"
        
        pending_bunny_proposals[proposal_id] = {
            "expert": expert,
            "email_data": email_data,
            "rich_html": rich_html,
            "saved_path": selector.save_proposal(proposal)
        }

        # Construir teclado interactivo de Telegram
        markup = InlineKeyboardMarkup()
        markup.row_width = 2
        markup.add(
            InlineKeyboardButton("✅ Aprobar Envío", callback_data=f"approve_{proposal_id}"),
            InlineKeyboardButton("❌ Descartar", callback_data=f"reject_{proposal_id}")
        )

        bot.send_message(message.chat.id, 
                f"🐇 <b>Propuesta Lista para Arconte (Bad Bunny)</b>\n\n"
                f"<b>Experto:</b> {html.escape(expert['name'])} ({html.escape(expert['country'])})\n"
                f"<b>Email:</b> <code>{html.escape(expert['email'])}</code>\n\n"
                f"<b>Asunto:</b> {html.escape(email_data['subject_local'])}\n\n"
                f"<b>Cuerpo (Castellano):</b>\n"
                f"<i>{html.escape(email_data['body_spanish'])}</i>\n\n"
                f"¿Autorizas el despliegue del correo?",
                parse_mode='HTML',
                reply_markup=markup
            )

    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Error crítico en la forja de Arconte: {str(e)}")

@bot.callback_query_handler(func=lambda call: call.data.startswith('approve_bunny_') or call.data.startswith('reject_bunny_'))
def handle_bunny_approval(call):
    if ALLOWED_USER_ID and str(call.from_user.id) != str(ALLOWED_USER_ID):
        return
        
    action, proposal_id = call.data.split('_', 1)
    # Reconstruir ID correctamente si fue cortado por split
    proposal_id = "bunny_" + proposal_id.split('_', 1)[1] if len(proposal_id.split('_')) > 1 else call.data.replace('approve_', '').replace('reject_', '')

    if proposal_id not in pending_bunny_proposals:
        bot.answer_callback_query(call.id, "❌ Esta propuesta ha expirado o ya fue procesada.")
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=call.message.text + "\n\n<i>(Propuesta Expirada)</i>", parse_mode='HTML')
        return
        
    proposal = pending_bunny_proposals[proposal_id]
    
    if call.data.startswith('reject'):
        bot.answer_callback_query(call.id, "Propuesta descartada.")
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, 
                              text=call.message.text + "\n\n❌ <b>DESCARTADO POR EL COO</b>", parse_mode='HTML')
        del pending_bunny_proposals[proposal_id]
        return
        
    # Lógica de Aprobación
    bot.answer_callback_query(call.id, "Aprobado. Desplegando...")
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, 
                          text=call.message.text + "\n\n⏳ <i>Desplegando en la red...</i>", parse_mode='HTML')
                          
    expert = proposal['expert']
    email_data = proposal['email_data']
    
    # Evaluar test mode
    destination_email = "elswork@gmail.com" if TEST_BUNNY_MODE else expert['email']
    mode_text = "⚠️ <b>[MODO TEST - ENVIADO A ELSWORK]</b>" if TEST_BUNNY_MODE else "✅ <b>[DESPLIEGUE OFICIAL]</b>"
    
    sender = EmailSender()
    
    formatted_body = email_data['body_local'].replace('\n', '<br>')
    body_html_direct = f"<div style='font-family: sans-serif; font-size: 14px; color: #333; line-height: 1.6;'>{formatted_body}</div>"
    
    success = sender.send_direct_email(
        to_email=destination_email,
        subject=email_data['subject_local'],
        body_html=body_html_direct,
        body_text=email_data['body_local']
    )
    
    if success:
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, 
                              text=call.message.text.replace("⏳ <i>Desplegando en la red...</i>", f"\n\n{mode_text} Desplegado con éxito a `{destination_email}`."), parse_mode='HTML')
    else:
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, 
                              text=call.message.text.replace("⏳ <i>Desplegando en la red...</i>", f"\n\n❌ Error en el servidor SMTP."), parse_mode='HTML')
                              
    del pending_bunny_proposals[proposal_id]

@bot.callback_query_handler(func=lambda call: call.data.startswith('approve_molt_') or call.data.startswith('reject_molt_'))
def handle_molt_approval(call):
    if ALLOWED_USER_ID and str(call.from_user.id) != str(ALLOWED_USER_ID):
        return
        
    action, post_id = call.data.split('_', 1)
    # Correct ID reconstruction
    post_id = post_id.split('_', 1)[1] if action == "approve" else post_id.split('_', 1)[1]

    if call.data.startswith('reject'):
        bot.answer_callback_query(call.id, "Propuesta descartada.")
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, 
                              text=call.message.text + "\n\n❌ <b>DESCARTADO</b>", parse_mode='HTML')
        return

    # Lógica de Aprobación para Moltbook
    bot.answer_callback_query(call.id, "Publicando en Moltbook...")
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, 
                          text=call.message.text + "\n\n⏳ <i>Accediendo a la matriz...</i>", parse_mode='HTML')

    proposal_file = f"/tmp/molt_proposal_{post_id}.json"
    if not os.path.exists(proposal_file):
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, 
                              text=call.message.text + "\n\n❌ Error: Propuesta expirada (archivo no encontrado).", parse_mode='HTML')
        return

    with open(proposal_file, "r") as f:
        proposal_data = json.load(f)
    
    comment_text = proposal_data['comment']
    
    # Intentar publicar
    API_KEY = "moltbook_sk_jTO_cK6BLuqpwgU0CAgnOZReUccM5xB3"
    BASE_URL = "https://www.moltbook.com/api/v1"
    HEADERS = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}
    
    try:
        # 1. Postear comentario
        res = requests.post(f"{BASE_URL}/posts/{post_id}/comments", headers=HEADERS, json={"content": comment_text})
        if res.status_code not in [200, 201]:
            raise Exception(f"Error API: {res.text}")
        
        data = res.json()
        comment_id = data['comment']['id']
        verification = data['comment'].get('verification')
        
        if verification:
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, 
                                  text=call.message.text + "\n\n🦞 <i>Reto anti-bot detectado. Resolviendo...</i>", parse_mode='HTML')
            
            # 2. Pedir a Athena que resuelva el reto
            challenge_text = verification['challenge_text']
            solve_prompt = f"Resuelve este reto matemático de Moltbook y responde SOLO con el número (con 2 decimales, ej 42.00): {challenge_text}"
            answer = brain.ask(solve_prompt, log_to_history=False).strip()
            
            # 3. Enviar verificación
            v_res = requests.post(f"{BASE_URL}/verify", headers=HEADERS, json={
                "verification_code": verification['verification_code'],
                "answer": answer
            })
            
            if v_res.status_code in [200, 201]:
                status_msg = f"✅ <b>¡Publicado y Verificado!</b>\n(Respuesta: {answer})"
            else:
                status_msg = f"⚠️ Publicado pero verificación fallida: {v_res.text}\n(Reto: {challenge_text})"
        else:
            status_msg = "✅ <b>Publicado directamente.</b>"

        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, 
                              text=call.message.text + f"\n\n{status_msg}", parse_mode='HTML')
        
        # Limpiar
        os.remove(proposal_file)

    except Exception as e:
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, 
                              text=call.message.text + f"\n\n❌ Error crítico: {str(e)}", parse_mode='HTML')

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
        DATABASE_URL = os.environ.get("DATABASE_URL", f"postgresql://arconte:{DB_PASSWORD}@synapse-ia-db:5432/synapse_ia")
        
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
        DATABASE_URL = os.environ.get("DATABASE_URL", f"postgresql://arconte:{DB_PASSWORD}@synapse-ia-db:5432/synapse_ia")
        
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

def auto_bunny_job():
    """Job to generate bunny proposal automatically."""
    print("🐇 Ejecutando auto-bunny (Directiva 3.0)...")
    if not ALLOWED_USER_ID:
        return
        
    # Simulate a message to reuse the logic
    class DummyMessage:
        def __init__(self):
            self.text = "/pasar_bunny"
            self.chat = type('Chat', (), {'id': int(ALLOWED_USER_ID)})()
            self.from_user = type('User', (), {'id': int(ALLOWED_USER_ID)})()
            
    pasar_bunny(DummyMessage())

def scheduler_loop():
    """Loop for all scheduled jobs."""
    # Since the container runs in CET (UTC+1), to run at 09:00 local Madrid time, 
    # we just use "09:00" assuming the base system time is correct.
    # The previous timezone parameter caused a crash on older schedule library versions.
    schedule.every().day.at("09:00").do(auto_bunny_job)
    schedule.every().day.at("21:00").do(auto_bunny_job)
    
    # Moltbook Heartbeat every 4 hours (to match cron and reduce noise)
    schedule.every(4).hours.do(execute_heartbeat)
    
    while True:
        schedule.run_pending()
        time.sleep(30)

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
    
    # Iniciar hilo del scheduler
    threading.Thread(target=scheduler_loop, daemon=True).start()
    
    bot.infinity_polling()
