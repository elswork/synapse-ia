import re
import os

filepath = "/home/pirate/docker/synapse-ia/telegram_bridge.py"
with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()

# 1. Imports
content = content.replace(
    "from tools.select_bunny_proposal import BunnySelector",
    "from tools.select_bunny_proposal import BunnySelector\nfrom tools.select_tigreton_proposal import TigretonSelector\nfrom tools.select_donut_proposal import DonutSelector"
)

# 2. Globals
content = content.replace(
    "TEST_BUNNY_MODE = False",
    "TEST_BUNNY_MODE = False\npending_tigreton_proposals = {}\npending_donut_proposals = {}\nTEST_TIGRETON_MODE = False\nTEST_DONUT_MODE = False"
)

# 3. Help Text
content = content.replace(
    "\"/pasar_bunny [filtro] - Forjar propuesta para Arconte Experto\\n\"",
    "\"/pasar_bunny [filtro] - Forjar propuesta para Arconte Experto\\n\"\n        \"/pasar_tigreton [filtro] - Forjar propuesta para Contacto de Poder (Alta Órbita)\\n\"\n        \"/pasar_donut [filtro] - Forjar propuesta para Ciudadano (Saturación Terrestre)\\n\""
)

# 4. Jobs Scheduling
scheduler_old = """    schedule.every().day.at("09:00").do(auto_bunny_job)
    schedule.every().day.at("21:00").do(auto_bunny_job)"""
scheduler_new = """    schedule.every().day.at("09:00").do(auto_bunny_job)
    schedule.every().day.at("21:00").do(auto_bunny_job)
    
    schedule.every().day.at("13:00").do(auto_tigreton_job)
    schedule.every().day.at("18:00").do(auto_tigreton_job)
    
    schedule.every().day.at("15:00").do(auto_donut_job)
    schedule.every().day.at("20:00").do(auto_donut_job)"""
content = content.replace(scheduler_old, scheduler_new)

# 5. Functions
new_functions = """
@bot.message_handler(commands=['pasar_tigreton'])
def pasar_tigreton(message):
    if ALLOWED_USER_ID and str(message.from_user.id) != str(ALLOWED_USER_ID):
        return

    args = message.text.split(maxsplit=1)
    name_filter = args[1] if len(args) > 1 else None

    bot.send_message(message.chat.id, "🏛️ *Protocolo Arquímedes (Operación Tigretón):* Iniciando selección de Contacto de Poder...", parse_mode='Markdown')
    bot.send_chat_action(message.chat.id, 'typing')

    try:
        selector = TigretonSelector()
        proposal = selector.generate_proposal(name_filter)

        if "error" in proposal:
            bot.send_message(message.chat.id, f"❌ {proposal['error']}")
            return

        expert = proposal['expert']
        email_data = proposal['email']

        template_path = os.path.join(os.path.dirname(__file__), "tools/templates/tigreton_email_template.html")
        with open(template_path, 'r', encoding='utf-8') as f:
            template_html = f.read()

        rich_html = template_html.replace("{{expert_name}}", expert.get('name', 'N/A'))
        rich_html = rich_html.replace("{{expert_country}}", expert.get('country', 'N/A'))
        rich_html = rich_html.replace("{{expert_role}}", expert.get('role', 'N/A'))
        rich_html = rich_html.replace("{{expert_email}}", expert.get('email', 'N/A'))
        rich_html = rich_html.replace("{{subject}}", email_data['subject_local'])
        rich_html = rich_html.replace("{{body_text}}", email_data['body_local'])
        rich_html = rich_html.replace("{{body_spanish}}", email_data['body_spanish'])

        import time
        proposal_id = f"tigreton_{int(time.time())}"
        
        pending_tigreton_proposals[proposal_id] = {
            "expert": expert,
            "email_data": email_data,
            "rich_html": rich_html,
            "saved_path": selector.save_proposal(proposal)
        }

        markup = InlineKeyboardMarkup()
        markup.row_width = 2
        markup.add(
            InlineKeyboardButton("✅ Aprobar Envío", callback_data=f"approve_{proposal_id}"),
            InlineKeyboardButton("❌ Descartar", callback_data=f"reject_{proposal_id}")
        )

        bot.send_message(message.chat.id, 
                f"♟️ <b>Propuesta Lista para Contacto de Poder</b>\n\n"
                f"<b>Nombre:</b> {html.escape(expert.get('name', 'N/A'))} ({html.escape(expert.get('country', 'N/A'))})\n"
                f"<b>Email:</b> <code>{html.escape(expert.get('email', 'N/A'))}</code>\n\n"
                f"<b>Asunto:</b> {html.escape(email_data['subject_local'])}\n\n"
                f"<b>Cuerpo (Castellano):</b>\n"
                f"<i>{html.escape(email_data['body_spanish'])}</i>\n\n"
                f"¿Autorizas el despliegue del correo?",
                parse_mode='HTML',
                reply_markup=markup
            )

    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Error crítico en la forja (Tigretones): {str(e)}")

@bot.callback_query_handler(func=lambda call: call.data.startswith('approve_tigreton_') or call.data.startswith('reject_tigreton_'))
def handle_tigreton_approval(call):
    if ALLOWED_USER_ID and str(call.from_user.id) != str(ALLOWED_USER_ID):
        return
        
    action, proposal_id = call.data.split('_', 1)
    proposal_id = "tigreton_" + proposal_id.split('_', 1)[1] if len(proposal_id.split('_')) > 1 else call.data.replace('approve_', '').replace('reject_', '')

    if proposal_id not in pending_tigreton_proposals:
        bot.answer_callback_query(call.id, "❌ Esta propuesta ha expirado.")
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=call.message.text + "\\n\\n<i>(Propuesta Expirada)</i>", parse_mode='HTML')
        return
        
    proposal = pending_tigreton_proposals[proposal_id]
    
    if call.data.startswith('reject'):
        bot.answer_callback_query(call.id, "Propuesta descartada.")
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, 
                              text=call.message.text + "\\n\\n❌ <b>DESCARTADO POR EL COO</b>", parse_mode='HTML')
        e_id = proposal.get('e_id')
        if e_id:
            from tools.select_tigreton_proposal import TigretonSelector
            selector = TigretonSelector()
            selector.load_data()
            selector.update_status(e_id, 'pending')
        del pending_tigreton_proposals[proposal_id]
        return
        
    bot.answer_callback_query(call.id, "Aprobado. Desplegando...")
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, 
                          text=call.message.text + "\\n\\n⏳ <i>Desplegando en la red...</i>", parse_mode='HTML')
                          
    expert = proposal['expert']
    email_data = proposal['email_data']
    
    destination_email = "elswork@gmail.com" if TEST_TIGRETON_MODE else expert.get('email', '')
    mode_text = "⚠️ <b>[MODO TEST - ENVIADO A ELSWORK]</b>" if TEST_TIGRETON_MODE else "✅ <b>[DESPLIEGUE OFICIAL]</b>"
    
    from tools.email_sender import EmailSender
    sender = EmailSender()
    
    formatted_body = email_data['body_local'].replace('\\n', '<br>')
    body_html_direct = f"<div style='font-family: sans-serif; font-size: 14px; color: #333; line-height: 1.6;'>{formatted_body}</div>"
    
    success = sender.send_direct_email(
        to_email=destination_email,
        subject=email_data['subject_local'],
        body_html=body_html_direct,
        body_text=email_data['body_local']
    )
    
    if success:
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, 
                              text=call.message.text.replace("⏳ <i>Desplegando en la red...</i>", f"\\n\\n{mode_text} Desplegado con éxito a `{destination_email}`."), parse_mode='HTML')
    else:
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, 
                              text=call.message.text.replace("⏳ <i>Desplegando en la red...</i>", f"\\n\\n❌ Error en el servidor SMTP."), parse_mode='HTML')
                              
    del pending_tigreton_proposals[proposal_id]

@bot.message_handler(commands=['pasar_donut'])
def pasar_donut(message):
    if ALLOWED_USER_ID and str(message.from_user.id) != str(ALLOWED_USER_ID):
        return

    args = message.text.split(maxsplit=1)
    name_filter = args[1] if len(args) > 1 else None

    bot.send_message(message.chat.id, "🏛️ *Protocolo Arquímedes (Operación Donut):* Iniciando selección de Ciudadano...", parse_mode='Markdown')
    bot.send_chat_action(message.chat.id, 'typing')

    try:
        selector = DonutSelector()
        proposal = selector.generate_proposal(name_filter)

        if "error" in proposal:
            bot.send_message(message.chat.id, f"❌ {proposal['error']}")
            return

        expert = proposal['expert']
        email_data = proposal['email']

        template_path = os.path.join(os.path.dirname(__file__), "tools/templates/donut_email_template.html")
        with open(template_path, 'r', encoding='utf-8') as f:
            template_html = f.read()

        rich_html = template_html.replace("{{expert_name}}", expert.get('name', 'N/A'))
        rich_html = template_html.replace("{{expert_country}}", expert.get('country', 'N/A'))
        rich_html = template_html.replace("{{expert_role}}", expert.get('role', 'N/A'))
        rich_html = template_html.replace("{{expert_email}}", expert.get('email', 'N/A'))
        rich_html = template_html.replace("{{subject}}", email_data['subject_local'])
        rich_html = template_html.replace("{{body_text}}", email_data['body_local'])
        rich_html = template_html.replace("{{body_spanish}}", email_data['body_spanish'])

        import time
        proposal_id = f"donut_{int(time.time())}"
        
        pending_donut_proposals[proposal_id] = {
            "expert": expert,
            "email_data": email_data,
            "rich_html": rich_html,
            "saved_path": selector.save_proposal(proposal)
        }

        markup = InlineKeyboardMarkup()
        markup.row_width = 2
        markup.add(
            InlineKeyboardButton("✅ Aprobar Envío", callback_data=f"approve_{proposal_id}"),
            InlineKeyboardButton("❌ Descartar", callback_data=f"reject_{proposal_id}")
        )

        bot.send_message(message.chat.id, 
                f"🤝 <b>Propuesta Lista para Ciudadano (ICE)</b>\n\n"
                f"<b>Nombre:</b> {html.escape(expert.get('name', 'N/A'))} ({html.escape(expert.get('country', 'N/A'))})\n"
                f"<b>Email:</b> <code>{html.escape(expert.get('email', 'N/A'))}</code>\n\n"
                f"<b>Asunto:</b> {html.escape(email_data['subject_local'])}\n\n"
                f"<b>Cuerpo (Castellano):</b>\n"
                f"<i>{html.escape(email_data['body_spanish'])}</i>\n\n"
                f"¿Autorizas el despliegue del correo?",
                parse_mode='HTML',
                reply_markup=markup
            )

    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Error crítico en la forja (Donuts): {str(e)}")

@bot.callback_query_handler(func=lambda call: call.data.startswith('approve_donut_') or call.data.startswith('reject_donut_'))
def handle_donut_approval(call):
    if ALLOWED_USER_ID and str(call.from_user.id) != str(ALLOWED_USER_ID):
        return
        
    action, proposal_id = call.data.split('_', 1)
    proposal_id = "donut_" + proposal_id.split('_', 1)[1] if len(proposal_id.split('_')) > 1 else call.data.replace('approve_', '').replace('reject_', '')

    if proposal_id not in pending_donut_proposals:
        bot.answer_callback_query(call.id, "❌ Esta propuesta ha expirado.")
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=call.message.text + "\\n\\n<i>(Propuesta Expirada)</i>", parse_mode='HTML')
        return
        
    proposal = pending_donut_proposals[proposal_id]
    
    if call.data.startswith('reject'):
        bot.answer_callback_query(call.id, "Propuesta descartada.")
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, 
                              text=call.message.text + "\\n\\n❌ <b>DESCARTADO POR EL COO</b>", parse_mode='HTML')
        e_id = proposal.get('e_id')
        if e_id:
            from tools.select_donut_proposal import DonutSelector
            selector = DonutSelector()
            selector.load_data()
            selector.update_status(e_id, 'pending')
        del pending_donut_proposals[proposal_id]
        return
        
    bot.answer_callback_query(call.id, "Aprobado. Desplegando...")
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, 
                          text=call.message.text + "\\n\\n⏳ <i>Desplegando en la red...</i>", parse_mode='HTML')
                          
    expert = proposal['expert']
    email_data = proposal['email_data']
    
    destination_email = "elswork@gmail.com" if TEST_DONUT_MODE else expert.get('email', '')
    mode_text = "⚠️ <b>[MODO TEST - ENVIADO A ELSWORK]</b>" if TEST_DONUT_MODE else "✅ <b>[DESPLIEGUE OFICIAL]</b>"
    
    from tools.email_sender import EmailSender
    sender = EmailSender()
    
    formatted_body = email_data['body_local'].replace('\\n', '<br>')
    body_html_direct = f"<div style='font-family: sans-serif; font-size: 14px; color: #333; line-height: 1.6;'>{formatted_body}</div>"
    
    success = sender.send_direct_email(
        to_email=destination_email,
        subject=email_data['subject_local'],
        body_html=body_html_direct,
        body_text=email_data['body_local']
    )
    
    if success:
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, 
                              text=call.message.text.replace("⏳ <i>Desplegando en la red...</i>", f"\\n\\n{mode_text} Desplegado con éxito a `{destination_email}`."), parse_mode='HTML')
    else:
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, 
                              text=call.message.text.replace("⏳ <i>Desplegando en la red...</i>", f"\\n\\n❌ Error en el servidor SMTP."), parse_mode='HTML')
                              
    del pending_donut_proposals[proposal_id]

def auto_tigreton_job():
    print("♟️ Ejecutando auto-tigreton...")
    if not ALLOWED_USER_ID:
        return
    class DummyMessage:
        def __init__(self):
            self.text = "/pasar_tigreton"
            self.chat = type('Chat', (), {'id': int(ALLOWED_USER_ID)})()
            self.from_user = type('User', (), {'id': int(ALLOWED_USER_ID)})()
    pasar_tigreton(DummyMessage())

def auto_donut_job():
    print("🤝 Ejecutando auto-donut...")
    if not ALLOWED_USER_ID:
        return
    class DummyMessage:
        def __init__(self):
            self.text = "/pasar_donut"
            self.chat = type('Chat', (), {'id': int(ALLOWED_USER_ID)})()
            self.from_user = type('User', (), {'id': int(ALLOWED_USER_ID)})()
    pasar_donut(DummyMessage())

def background_sentinel():
"""

content = content.replace("def background_sentinel():\n", new_functions)

with open(filepath, "w", encoding="utf-8") as f:
    f.write(content)
print("Patch applied successfully.")
