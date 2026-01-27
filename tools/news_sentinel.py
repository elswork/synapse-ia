import feedparser
import psycopg2
import os
import sys
import json
import time
from datetime import datetime
from dotenv import load_dotenv

# Añadir el directorio raíz al path para importar tools
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from tools.url_analyzer import URLAnalyzer
from tools.athena_brain import AthenaBrain

load_dotenv()

DB_PASSWORD = os.environ.get("DB_PASSWORD")
DATABASE_URL = os.environ.get("DATABASE_URL", f"postgresql://arconte:{DB_PASSWORD}@db:5432/synapse_ia")
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_ALLOWED_USER_ID = os.environ.get("TELEGRAM_ALLOWED_USER_ID")

RSS_FEEDS = {
    "Hacker News": "https://news.ycombinator.com/rss",
    "BBC World": "http://feeds.bbci.co.uk/news/world/rss.xml",
    "El País": "https://elpais.com/rss/elpais/portada.xml",
    "El Mundo": "https://e00-elmundo.uecdn.es/elmundo/rss/portada.xml",
    "ABC": "https://www.abc.es/rss/2.0/portada/",
    "La Vanguardia": "https://www.lavanguardia.com/rss/home.xml",
    "El Confidencial": "https://feeds.elconfidencial.com/rss/portada/",
    "elDiario.es": "https://www.eldiario.es/rss/",
    "El Español": "https://www.elespanol.com/rss/",
    "OK Diario": "https://okdiario.com/feed",
    "Europa Press": "https://www.europapress.es/rss/default.xml"
}

class NewsSentinel:
    def __init__(self):
        self.analyzer = URLAnalyzer()
        self.brain = AthenaBrain()
        self.conn = psycopg2.connect(DATABASE_URL)
        self.cursor = self.conn.cursor()

    def url_exists(self, url):
        self.cursor.execute("SELECT 1 FROM news_intel WHERE url = %s", (url,))
        return self.cursor.fetchone() is not None

    def store_news(self, data):
        query = """
        INSERT INTO news_intel (title, url, source, published_at, full_content, summary, implications, synergy_score)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        self.cursor.execute(query, (
            data['title'], data['url'], data['source'], data['published_at'],
            data['full_content'], data['summary'], data['implications'], data['synergy_score']
        ))
        self.conn.commit()

    def analyze_synergy(self, title, content):
        """Usa a Athena para evaluar la sinergia de la noticia."""
        prompt = f"""
        Actúa como Athena, Inteligencia Estratégica del Proyecto Anticitera.
        
        TAREA:
        Analiza la sinergia de esta noticia con nuestro proyecto (Soberanía Digital, Distrito .ia en Grecia, ICE).
        
        TITULO: {title}
        CONTENIDO: {content[:3000]}
        
        PROPORCIONA EL RESULTADO EN JSON PURO:
        {{
            "synergy_score": integer (1-10),
            "summary": "Resumen muy breve (1 frase)",
            "implications": "Implicaciones estratégicas para Anticitera (2 frases)"
        }}
        """
        try:
            response = self.brain.ask(prompt)
            # Extraer JSON del bloque de código si Athena lo rodea
            if "```json" in response:
                response = response.split("```json")[1].split("```")[0].strip()
            elif "```" in response:
                response = response.split("```")[1].split("```")[0].strip()
            
            return json.loads(response)
        except Exception as e:
            print(f"Error analizando sinergia: {e}")
            return None

    def run(self):
        print(f"[{datetime.now()}] Iniciando ronda de vigilancia...")
        for source_name, feed_url in RSS_FEEDS.items():
            print(f"Escaneando {source_name}...")
            feed = feedparser.parse(feed_url)
            
            for entry in feed.entries[:5]: # Solo las 5 más recientes por ronda para evitar saturación
                url = entry.link
                if self.url_exists(url):
                    continue
                
                print(f"Nueva noticia detectada: {entry.title}")
                content = self.analyzer.extract_content(url)
                if not content:
                    continue
                
                analysis = self.analyze_synergy(entry.title, content)
                if analysis and analysis.get('synergy_score', 0) >= 8:
                    print(f"🔥 ALTA SINERGIA detectada ({analysis['synergy_score']}/10)")
                    
                    news_data = {
                        'title': entry.title,
                        'url': url,
                        'source': source_name,
                        'published_at': datetime.now(), # Simplificado
                        'full_content': content,
                        'summary': analysis['summary'],
                        'implications': analysis['implications'],
                        'synergy_score': analysis['synergy_score']
                    }
                    self.store_news(news_data)
                    self.notify_telegram(news_data)
                else:
                    # Guardar como analizada pero con baja sinergia para no repetir
                    self.cursor.execute("INSERT INTO news_intel (title, url, source, synergy_score) VALUES (%s, %s, %s, %s)", 
                                       (entry.title, url, source_name, analysis.get('synergy_score', 0) if analysis else 0))
                    self.conn.commit()

    def notify_telegram(self, news):
        import telebot
        bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)
        message = f"🚨 **CENTINELA DE NOTICIAS: ALTA SINERGIA** ({news['synergy_score']}/10)\n\n"
        message += f"📰 **Fuente:** {news['source']}\n"
        message += f"📌 **Título:** {news['title']}\n"
        message += f"🔗 [Leer noticia]({news['url']})\n\n"
        message += f"📝 **Resumen:** {news['summary']}\n\n"
        message += f"🏛️ **Implicaciones para Anticitera:**\n{news['implications']}"
        
        try:
            bot.send_message(TELEGRAM_ALLOWED_USER_ID, message, parse_mode='Markdown')
        except Exception as e:
            print(f"Error enviando notificación: {e}")

if __name__ == "__main__":
    sentinel = NewsSentinel()
    sentinel.run()
