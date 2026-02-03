import google.generativeai as genai
from core_v2.domain.interfaces.strategic_consultant import IStrategicConsultant

class GeminiAthenaAdapter(IStrategicConsultant):
    def __init__(self, api_key: str, model_name: str = "gemini-3-flash-preview"):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model_name)

    def ask(self, prompt: str, log_to_history: bool = True) -> str:
        # In a full hexagonal implementation, the identity/system prompt 
        # would be injected from a Domain Service or Repository
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"Error in Gemini consultation: {str(e)}"

    def analyze_risk(self, context: str) -> dict:
        # Simplified risk analysis for core redesign phase
        prompt = f"Analyze structural risks for the following context: {context}. Return JSON."
        response = self.ask(prompt, log_to_history=False)
        return {"response": response} # Logic to parse JSON would go here
