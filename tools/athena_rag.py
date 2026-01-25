import os
import sqlite3
from tools.embeddings_manager import EmbeddingsManager

class AthenaRAG:
    def __init__(self, base_path=None):
        self.base_path = base_path or os.environ.get("BASE_PATH", "/app")
        self.manager = EmbeddingsManager(self.base_path)
        self.db_path = os.path.join(self.base_path, "context/synapse_memory.db")
        self.history_path = os.path.join(self.base_path, "context/history.md")

    def sync_index(self):
        """Indexa tanto el history.md como la base de datos de eventos."""
        documents = []
        
        # 1. Leer History.md (por secciones ##)
        if os.path.exists(self.history_path):
            with open(self.history_path, 'r') as f:
                content = f.read()
                sections = content.split('## ')
                for sec in sections:
                    if sec.strip():
                        documents.append({
                            "source": "history.md",
                            "content": f"## {sec.strip()}"
                        })

        # 2. Leer Eventos de PostgreSQL
        db_url = os.environ.get("DATABASE_URL")
        if db_url:
            try:
                import psycopg2
                conn = psycopg2.connect(db_url)
                cursor = conn.cursor()
                cursor.execute("SELECT agent, event_type, description, timestamp FROM events")
                rows = cursor.fetchall()
                for row in rows:
                    documents.append({
                        "source": "postgres_events",
                        "content": f"Agente: {row[0]} | Tipo: {row[1]} | Desc: {row[2]}",
                        "timestamp": str(row[3])
                    })
                cursor.close()
                conn.close()
            except Exception as e:
                print(f"Error al leer de PostgreSQL para RAG: {e}")

        if documents:
            print(f"Sincronizando índice vectorial con {len(documents)} fragmentos...")
            self.manager.create_index(documents)

    def search_context(self, query):
        """Devuelve el contexto relevante para una consulta."""
        results = self.manager.search(query)
        context = "\n--- MEMORIA RELEVANTE RECUPERADA ---\n"
        for res in results:
            m = res['metadata']
            context += f"Fuente: {m['source']} | Score: {res['score']:.4f}\nContenido: {m['content']}\n\n"
        return context

if __name__ == "__main__":
    rag = AthenaRAG()
    rag.sync_index()
    print(rag.search_context("¿Qué se dijo sobre la IANA?"))
