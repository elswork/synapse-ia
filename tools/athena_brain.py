import os
from openai import OpenAI
from nexus_sync import NexusSync

class AthenaBrain:
    def __init__(self, base_path="/home/pirate/docker/synapse-ia"):
        self.base_path = base_path
        self.client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
        self.prompt_path = os.path.join(base_path, "prompts/athena.md")
        self.syncer = NexusSync(base_path)

    def load_identity(self):
        with open(self.prompt_path, "r") as f:
            return f.read()

    def ask(self, question, context_files=[]):
        """Envía una consulta a la 'Athena Real' usando el API de OpenAI."""
        identity = self.load_identity()
        
        # Ingesta de archivos de contexto si se proporcionan
        context_data = ""
        for f_path in context_files:
            full_path = os.path.join(self.base_path, f_path)
            if os.path.exists(full_path):
                with open(full_path, "r") as f:
                    context_data += f"\n--- ARCHIVO: {f_path} ---\n{f.read()}\n"

        messages = [
            {"role": "system", "content": identity},
            {"role": "user", "content": f"Contexto Adicional:\n{context_data}\n\nPregunta: {question}"}
        ]

        try:
            print("Conectando con el Oráculo (Athena)...")
            response = self.client.chat.completions.create(
                model="gpt-4o", # O el modelo definido en el entorno
                messages=messages,
                temperature=0.7
            )
            athena_response = response.choices[0].message.content
            
            # Registrar en el historial
            self.syncer.log_event("ATHENA_REAL", "LIVE_CONSULTATION", f"Consulta: {question}\nRespuesta: {athena_response}")
            return athena_response
        except Exception as e:
            return f"Error al conectar con Athena: {str(e)}"

if __name__ == "__main__":
    # Test opcional
    brain = AthenaBrain()
    # print(brain.ask("¿Cuál es tu visión sobre el estado actual del Dossier para ELOT?"))
