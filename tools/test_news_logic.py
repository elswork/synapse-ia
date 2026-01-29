import json
import sys
import os

# Append current directory to path
sys.path.append("/home/pirate/docker/synapse-ia")
from tools.news_sentinel import NewsSentinel

def test_news_sentinel():
    # Set BASE_PATH for local execution
    os.environ["BASE_PATH"] = "/home/pirate/docker/synapse-ia"
    sentinel = NewsSentinel()
    
    test_cases = [
        {
            "title": "OpenAI launches new GPT-5 model with improved reasoning",
            "content": "OpenAI has announced the release of GPT-5, featuring advanced reasoning capabilities and a larger context window. The model is available for ChatGPT Plus users today..."
        },
        {
            "title": "Greece establishes new digital tech district with focus on international identity",
            "content": "The Greek government is launching a new administrative district focused on digital innovation. This follows discussions on how to better integrate digital sovereignty within the EU framework..."
        },
        {
            "title": "European Citizens' Initiative on Digital Sovereignty gains momentum",
            "content": "A new ECI proposal is calling for strict enforcement of digital identity standards across all member states, aiming to reduce dependence on foreign technology providers..."
        }
    ]
    
    for case in test_cases:
        print(f"\n--- Testing: {case['title']} ---")
        analysis = sentinel.analyze_synergy(case['title'], case['content'])
        print(json.dumps(analysis, indent=2))
        print(f"Verdict: {analysis.get('verdict')}")

if __name__ == "__main__":
    test_news_sentinel()
