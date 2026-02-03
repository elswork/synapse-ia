from core_v2.domain.interfaces.sovereign_memory import ISovereignMemory
from core_v2.domain.interfaces.news_scraper import INewsScraper
from core_v2.domain.interfaces.synergy_analyzer import ISynergyAnalyzer

class SyncNewsUseCase:
    def __init__(self, memory: ISovereignMemory, scraper: INewsScraper, analyzer: ISynergyAnalyzer):
        self.memory = memory
        self.scraper = scraper
        self.analyzer = analyzer

    def execute(self):
        latest_news = self.scraper.fetch_latest()
        for news in latest_news:
            # Simple check if URL exists could be added here or in the scraper
            analyzed_news = self.analyzer.analyze(news)
            if analyzed_news.synergy_score >= 8.5:
                self.memory.save_news(analyzed_news)
                # Here we could also trigger notifications (another adapter)
