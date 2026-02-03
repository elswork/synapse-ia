import telebot
from core_v2.application.get_telemetry import GetTelemetryUseCase
from core_v2.application.add_goal import AddGoalUseCase

class TelegramInputAdapter:
    def __init__(self, token: str, allowed_id: str, telemetry_case: GetTelemetryUseCase, goal_case: AddGoalUseCase):
        self.bot = telebot.TeleBot(token)
        self.allowed_id = allowed_id
        self.telemetry_case = telemetry_case
        self.goal_case = goal_case
        self._setup_handlers()

    def _setup_handlers(self):
        @self.bot.message_handler(commands=['telemetria'])
        def handle_telemetry(message):
            if str(message.from_user.id) == self.allowed_id:
                report = self.telemetry_case.execute()
                self.bot.reply_to(message, report, parse_mode='Markdown')

        @self.bot.message_handler(commands=['todo'])
        def handle_todo(message):
            if str(message.from_user.id) == self.allowed_id:
                parts = message.text.split(maxsplit=1)
                if len(parts) > 1:
                    result = self.goal_case.execute(parts[1])
                    self.bot.reply_to(message, result)

    def start(self):
        print("🏛️ Nexo Core V2 Input (Telegram) escuchando...")
        self.bot.infinity_polling()
