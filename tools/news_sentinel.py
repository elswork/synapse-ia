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
        # Usamos flash para el centinela (ahorro de costes masivo)
        self.brain = AthenaBrain(model_name="gemini-1.5-flash")
        self.conn = psycopg2.connect(DATABASE_URL)
        self.cursor = self.conn.cursor()
        
        # Palabras clave de alta relevancia para Anticitera
        self.relevant_keywords = [
            "soberanía", "sovereignty", "anticitera", "antikythera", "grecia", "greece", 
            "ia ", " ai ", "artificial intelligence", "inteligencia artificial", 
            "europe", "ue ", " bruselas", "brussels", "privacidad", "privacy", 
            "regulation", "regulación", "normativa", "standard", "estándar", "iso", 
            "semiconductor", "chip", "cuántica", "quantum", "ciberseguridad", "cybersecurity",
            "digital rights", "derechos digitales", "ice", "iniciativa ciudadana", 
            ".ia", "domain", "dominio", "iana", "icann"
        ]

    def is_relevant_title(self, title):
        """Filtro rápido basado en palabras clave para evitar costes de IA en noticias basura."""
        title_lower = title.lower()
        return any(kw in title_lower for kw in self.relevant_keywords)

    def url_exists(self, url):
        self.cursor.execute("SELECT 1 FROM news_intel WHERE url = %s", (url,))
        return self.cursor.fetchone() is not None

    def store_news(self, data):
        query = """
        INSERT INTO news_intel (title, url, source, published_at, full_content, summary, implications, synergy_score, is_approved)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING id
        """
        self.cursor.execute(query, (
            data['title'], data['url'], data['source'], data['published_at'],
            data['full_content'], data['summary'], data['implications'], data['synergy_score'],
            False  # is_approved default to False
        ))
        new_id = self.cursor.fetchone()[0]
        self.conn.commit()
        return new_id

    def analyze_synergy(self, title, content):
        """Usa a Athena para evaluar la sinergia de la noticia con una matriz multidimensional."""
        prompt = f"""
        Actúa como Athena, Inteligencia Estratégica del Proyecto Anticitera.
        
        TAREA:
        Evalúa la sinergia de esta noticia con nuestro proyecto mediante una matriz de puntuación estricta (1-10).
        
        DIMENSIONES DE EVALUACIÓN:
        1. Soberanía Administrativa/ISO: Relevancia para el distrito .ia en Grecia, trámites ISO 3166-1 o estandarización internacional.
        2. Derechos Digitales/ICE: Relevancia directa para la Iniciativa Ciudadana Europea, privacidad en la UE o soberanía tecnológica ciudadana.
        3. Inteligencia Geopolítica: Cambios regulatorios o políticos que afecten directamente la operación de nuestros nodos o la viabilidad de la nación digital.

        CRITERIOS DE EXCLUSIÓN (PUNTUAR 0 SI):
        - Noticias tecnológicas genéricas (lanzamientos de hardware, modelos de IA comerciales como OpenAI/Google sin implicación soberana).
        - IA generativa trivial (arte, chatbots, entretenimiento).
        - Noticias sin impacto en el marco europeo o griego (salvo cambio geopolítico global masivo).

        NOTICIA A ANALIZAR:
        TITULO: {title}
        CONTENIDO: {content[:3000]}
        
        RETORNA ÚNICAMENTE UN OBJETO JSON:
        {{
            "scores": {{
                "iso_sovereignty": integer,
                "eu_digital_rights": integer,
                "geopolitical_intel": integer
            }},
            "average_score": float,
            "summary": "Resumen ejecutivo (1 frase)",
            "implications": "Impacto táctico para Anticitera (2 frases)",
            "verdict": "APROBADO/RECHAZADO"
        }}
        """
        try:
            # Desactivamos el log en history.md para el análisis de sinergia para evitar bloat
            response = self.brain.ask(prompt, log_to_history=False)
            # Limpieza de la respuesta para asegurar JSON válido
            if "```json" in response:
                response = response.split("```json")[1].split("```")[0].strip()
            elif "```" in response:
                response = response.split("```")[1].split("```")[0].strip()
            
            data = json.loads(response)
            # Asegurar que el veredicto se basa en un umbral estricto (media >= 8.5 o algún eje == 10)
            avg = data.get('average_score', 0)
            max_score = max(data.get('scores', {}).values()) if data.get('scores') else 0
            
            if avg >= 8.5 or max_score == 10:
                data['verdict'] = "APROBADO"
            else:
                data['verdict'] = "RECHAZADO"
            
            return data
        except Exception as e:
            print(f"Error analizando sinergia: {e}")
            return None

    def run(self):
        print(f"[{datetime.now()}] Iniciando ronda de vigilancia (Modo Económico)...")
        for source_name, feed_url in RSS_FEEDS.items():
            print(f"Escaneando {source_name}...")
            feed = feedparser.parse(feed_url)
            
            # Solo las 3 más recientes por ronda (antes 5)
            for entry in feed.entries[:3]: 
                url = entry.link
                if self.url_exists(url):
                    continue
                
                # PRE-FILTRO DE RELEVANCIA
                if not self.is_relevant_title(entry.title):
                    print(f"⏩ Saltando noticia irrelevante: {entry.title}")
                    # Registramos el salto para no volver a evaluarla
                    self.cursor.execute("INSERT INTO news_intel (title, url, source, synergy_score) VALUES (%s, %s, %s, %s)", 
                                       (entry.title, url, source_name, 0.0))
                    self.conn.commit()
                    continue

                print(f"📍 Alta relevancia potencial detectada: {entry.title}")
                content = self.analyzer.extract_content(url)
                if not content:
                    continue
                
                analysis = self.analyze_synergy(entry.title, content)
                if analysis and analysis.get('verdict') == "APROBADO":
                    print(f"🔥 ALTA SINERGIA detectada (Media: {analysis['average_score']}/10)")
                    
                    news_data = {
                        'title': entry.title,
                        'url': url,
                        'source': source_name,
                        'published_at': datetime.now(), # Simplificado
                        'full_content': content,
                        'summary': analysis['summary'],
                        'implications': analysis['implications'],
                        'synergy_score': analysis['average_score']
                    }
                    news_id = self.store_news(news_data)
                    news_data['id'] = news_id
                    news_data['detailed_scores'] = analysis['scores']
                    self.notify_telegram(news_data)
                else:
                    # Guardar como analizada pero con baja sinergia para no repetir
                    score = analysis.get('average_score', 0) if analysis else 0
                    self.cursor.execute("INSERT INTO news_intel (title, url, source, synergy_score) VALUES (%s, %s, %s, %s)", 
                                       (entry.title, url, source_name, score))
                    self.conn.commit()

    def notify_telegram(self, news):
        import telebot
        bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)
        scores = news.get('detailed_scores', {})
        
        message = f"🚨 **CENTINELA DE HIERRO: ALTA SINERGIA**\n\n"
        message += f"📊 **Puntuación Media:** `{news['synergy_score']}/10`\n"
        message += f"🔹 ISO: `{scores.get('iso_sovereignty', 0)}` | 🔹 EU: `{scores.get('eu_digital_rights', 0)}` | 🔹 Geo: `{scores.get('geopolitical_intel', 0)}`\n\n"
        message += f"🆔 **ID:** `{news['id']}`\n"
        message += f"📰 **Fuente:** {news['source']}\n"
        message += f"📌 **Título:** {news['title']}\n"
        message += f"🔗 [Leer noticia]({news['url']})\n\n"
        message += f"📝 **Resumen:** {news['summary']}\n\n"
        message += f"🏛️ **Implicaciones para Anticitera:**\n{news['implications']}\n\n"
        message += f"✅ Para aprobar y persistir: `/aprobar {news['id']}`"
        
        try:
            bot.send_message(TELEGRAM_ALLOWED_USER_ID, message, parse_mode='Markdown')
        except Exception as e:
            print(f"Error enviando notificación: {e}")

if __name__ == "__main__":
    sentinel = NewsSentinel()
    sentinel.run()
