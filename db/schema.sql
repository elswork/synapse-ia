-- Schema for News Intelligence
CREATE TABLE IF NOT EXISTS news_intel (
    id SERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    url TEXT UNIQUE NOT NULL,
    source VARCHAR(100),
    published_at TIMESTAMP,
    full_content TEXT,
    summary TEXT,
    implications TEXT,
    synergy_score INTEGER,
    notified BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Index for URL uniqueness and performance
CREATE INDEX IF NOT EXISTS idx_news_url ON news_intel(url);
