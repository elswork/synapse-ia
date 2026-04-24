import os
import google.generativeai as genai
from dotenv import load_dotenv
from nexus_sync import NexusSync

class AthenaBrain:
    def __init__(self, base_path=None, model_name="gemini-2.0-flash"):
        self.base_path = base_path or os.environ.get("BASE_PATH", "/app")
        load_dotenv(os.path.join(self.base_path, ".env"))
        
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY no encontrada en el entorno.")
            
        genai.configure(api_key=api_key)
        self.model_name = model_name
        self.model = genai.GenerativeModel(self.model_name)
        self.prompt_path = os.path.join(self.base_path, "prompts/athena.md")
        self.syncer = NexusSync(self.base_path)

    def load_identity(self):
        with open(self.prompt_path, "r") as f:
            return f.read()

    def ask(self, question, context_files=[], log_to_history=True, model_override=None):
        """Envía una consulta a la 'Athena Real' usando RAG y contexto de archivos."""
        
        # Selección de modelo dinámica
        current_model = self.model
        if model_override and model_override != self.model_name:
            print(f"DEBUG: Usando modelo override: {model_override}")
            current_model = genai.GenerativeModel(model_override)
            
        identity = self.load_identity()
        
        # 1. Recuperación de Memoria Semántica (RAG)
        try:
            from tools.athena_rag import AthenaRAG
            rag = AthenaRAG(self.base_path)
            semantic_context = rag.search_context(question)
        except Exception as e:
            semantic_context = f"Error al recuperar memoria semántica: {e}"
        
        # 2. Ingesta de archivos de contexto manuales
        context_data = ""
        for f_path in context_files:
            # ... (Lógica de archivos manuales se mantiene igual)
            if os.path.isabs(f_path):
                full_path = f_path
            else:
                full_path = os.path.join(self.base_path, f_path)
                
            if os.path.exists(full_path):
                with open(full_path, "r") as f:
                    context_data += f"\n--- ARCHIVO MANUAL: {f_path} ---\n{f.read()}\n"

        full_prompt = f"""
SÍGUELAS SIEMPRE:
{identity}

{semantic_context}

CONTEXTO ADICIONAL (ARCHIVOS):
{context_data}

INSTRUCCIÓN ADICIONAL: Responde SIEMPRE en CASTELLANO, manteniendo el tono diplomático y estratégico definido.

PREGUNTA DEL USUARIO: {question}
"""

        try:
            print(f"Consultando al Oráculo ({current_model.model_name}) con Memoria Semántica Activa...")
            response = current_model.generate_content(full_prompt)
            athena_response = response.text
            
            # Registrar en el historial (opcional)
            self.syncer.log_event("ATHENA_REAL", "RAG_CONSULTATION", f"Consulta: {question}\nRespuesta: {athena_response}", log_to_md=log_to_history)
            return athena_response
        except Exception as e:
            return f"Error al conectar con Athena (Gemini): {str(e)}"

if __name__ == "__main__":
    brain = AthenaBrain()
    print("🧠 Nexus Synapse-IA Activo y en escucha...")
    # Bucle infinito para mantener el contenedor vivo
    import time
    while True:
        time.sleep(3600)
