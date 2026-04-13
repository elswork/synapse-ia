import os
import json
import numpy as np
import google.generativeai as genai
from dotenv import load_dotenv

class EmbeddingsManager:
    def __init__(self, base_path=None):
        self.base_path = base_path or os.environ.get("BASE_PATH", "/app")
        load_dotenv(os.path.join(base_path, ".env"))
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY no encontrada.")
        
        genai.configure(api_key=api_key)
        self.index_path = os.path.join(base_path, "context/vector_index.json")
        self.embeddings_path = os.path.join(base_path, "context/embeddings.npy")
        
    def get_embedding(self, text):
        """Obtiene el embedding de un texto usando Gemini."""
        result = genai.embed_content(
            model="models/embedding-001",
            content=text,
            task_type="retrieval_document"
        )
        return result['embedding']

    def create_index(self, documents):
        """Crea un índice local de vectores."""
        embeddings = []
        metadata = []
        
        for doc in documents:
            print(f"Indexando: {doc['source']}...")
            emb = self.get_embedding(doc['content'])
            embeddings.append(emb)
            metadata.append({
                "source": doc['source'],
                "content": doc['content'],
                "timestamp": doc.get('timestamp', '')
            })
            
        # Guardar en disco
        np.save(self.embeddings_path, np.array(embeddings))
        with open(self.index_path, 'w') as f:
            json.dump(metadata, f, indent=2)
        print("Índice vectorial creado con éxito.")

    def search(self, query, top_k=3):
        """Busca los fragmentos más relevantes."""
        if not os.path.exists(self.embeddings_path):
            return []
            
        query_emb = self.get_embedding(query)
        embeddings = np.load(self.embeddings_path)
        with open(self.index_path, 'r') as f:
            metadata = json.load(f)
            
        # Similitud Coseno simplificada (dot product si están normalizados)
        # Gemini embeddings suelen venir normalizados
        similarities = np.dot(embeddings, query_emb)
        top_indices = np.argsort(similarities)[::-1][:top_k]
        
        results = []
        for idx in top_indices:
            results.append({
                "score": float(similarities[idx]),
                "metadata": metadata[idx]
            })
        return results

if __name__ == "__main__":
    # Test simple
    manager = EmbeddingsManager()
    # manager.create_index([{"source": "test", "content": "Anticitera es una isla griega."}])
    # print(manager.search("¿Dónde está Anticitera?"))
