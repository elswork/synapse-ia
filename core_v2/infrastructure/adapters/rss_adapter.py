import feedparser
from typing import List
from core_v2.domain.interfaces.news_scraper import INewsScraper
from core_v2.domain.models.news import News

class RSSScraperAdapter(INewsScraper):
    def __init__(self, feeds: dict):
        self.feeds = feeds

    def fetch_latest(self) -> List[News]:
        all_news = []
        for source, url in self.feeds.items():
            feed = feedparser.parse(url)
            for entry in feed.entries[:5]:
                all_news.append(News(
                    id=0, # Temporary ID
                    title=entry.title,
                    url=entry.link,
                    source=source,
                    summary=entry.get("summary", "")
                ))
        return all_news
