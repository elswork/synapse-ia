import json
from ...domain.interfaces.synergy_analyzer import ISynergyAnalyzer
from ...domain.models.news import News
# Assuming we can import from the parent tools directory once path is set
# from tools.athena_brain import AthenaBrain 

class AthenaSynergyAdapter(ISynergyAnalyzer):
    def __init__(self, athena_brain):
        self.brain = athena_brain

    def analyze(self, news: News) -> News:
        prompt = f"Analyze synergy for: {news.title}\nContent: {news.summary}" # Simplified for now
        response = self.brain.ask(prompt, log_to_history=False)
        # Logic to parse JSON from Athena response
        try:
            if "```json" in response:
                response = response.split("```json")[1].split("```")[0].strip()
            data = json.loads(response)
            news.synergy_score = data.get("average_score", 0)
            news.implications = data.get("implications", "")
        except:
             pass
        return news
