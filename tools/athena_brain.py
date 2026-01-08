import os
import google.generativeai as genai
from dotenv import load_dotenv
from nexus_sync import NexusSync

class AthenaBrain:
    def __init__(self, base_path="/home/pirate/docker/synapse-ia"):
        self.base_path = base_path
        load_dotenv(os.path.join(base_path, ".env"))
        
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY no encontrada en el entorno.")
            
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel("gemini-3-flash")
        self.prompt_path = os.path.join(base_path, "prompts/athena.md")
        self.syncer = NexusSync(base_path)

    def load_identity(self):
        with open(self.prompt_path, "r") as f:
            return f.read()

    def ask(self, question, context_files=[]):
        """Envía una consulta a la 'Athena Real' usando el API de Google Gemini."""
        identity = self.load_identity()
        
        # Ingesta de archivos de contexto if provided
        context_data = ""
        for f_path in context_files:
            # Handle absolute paths or relative to base_path
            if os.path.isabs(f_path):
                full_path = f_path
            else:
                full_path = os.path.join(self.base_path, f_path)
                
            if os.path.exists(full_path):
                with open(full_path, "r") as f:
                    context_data += f"\n--- ARCHIVO: {f_path} ---\n{f.read()}\n"

        full_prompt = f"""
SÍGUELAS SIEMPRE:
{identity}

CONTEXTO DEL PROYECTO:
{context_data}

INSTRUCCIÓN ADICIONAL: Responde SIEMPRE en CASTELLANO, manteniendo el tono diplomático y estratégico definido.

PREGUNTA DEL USUARIO: {question}
"""

        try:
            print("Conectando con el Oráculo Real (Athena/Gemini)...")
            response = self.model.generate_content(full_prompt)
            athena_response = response.text
            
            # Registrar en el historial
            self.syncer.log_event("ATHENA_REAL", "LIVE_GEMINI_SYNC", f"Consulta: {question}\nRespuesta: {athena_response}")
            return athena_response
        except Exception as e:
            return f"Error al conectar con Athena (Gemini): {str(e)}"

if __name__ == "__main__":
    brain = AthenaBrain()
    # print(brain.ask("¿Estás conectada, Athena?"))
