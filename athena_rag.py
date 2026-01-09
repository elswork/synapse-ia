import os
import sqlite3
from tools.embeddings_manager import EmbeddingsManager

class AthenaRAG:
    def __init__(self, base_path="/home/pirate/docker/synapse-ia"):
        self.base_path = base_path
        self.manager = EmbeddingsManager(base_path)
        self.db_path = os.path.join(base_path, "context/synapse_memory.db")
        self.history_path = os.path.join(base_path, "context/history.md")

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

        # 2. Leer Eventos de SQLite
        if os.path.exists(self.db_path):
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT agent, event_type, description, timestamp FROM events")
            rows = cursor.fetchall()
            for row in rows:
                documents.append({
                    "source": "sqlite_events",
                    "content": f"Agente: {row[0]} | Tipo: {row[1]} | Desc: {row[2]}",
                    "timestamp": row[3]
                })
            conn.close()

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
    # rag.sync_index()
    # print(rag.search_context("¿Qué se dijo sobre la IANA?"))
