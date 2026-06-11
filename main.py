import os
import feedparser
import requests
from bs4 import BeautifulSoup

# ==========================
# GitHub Secrets
# ==========================

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

# ==========================
# Duplicate Filter
# ==========================

POSTED_FILE = "posted_news.txt"

if not os.path.exists(POSTED_FILE):
    open(POSTED_FILE, "w", encoding="utf-8").close()

def get_posted_news():
    with open(POSTED_FILE, "r", encoding="utf-8") as f:
        return set(f.read().splitlines())

def save_news(title):
    with open(POSTED_FILE, "a", encoding="utf-8") as f:
        f.write(title + "\n")

# ==========================
# Category Detection
# ==========================

def detect_category(title):

    title = title.lower()

    if "transfer" in title:
        return "🔄 Transfer News"

    elif "injury" in title:
        return "🏥 Injury News"

    elif "manager" in title:
        return "👔 Manager News"

    elif "contract" in title:
        return "📝 Contract News"

    elif "premier league" in title:
        return "🏆 Premier League"

    return "⚽ Football News"

# ==========================
# RSS Sources
# ==========================

rss_feeds = [
    "https://feeds.bbci.co.uk/sport/football/rss.xml",
    "https://www.skysports.com/rss/12040",
    "https://news.google.com/rss/search?q=football"
]

# ==========================
# Daily Limit
# ==========================

MAX_POSTS = 10
posted_today = 0

posted_news = get_posted_news()

# ==========================
# Main Loop
# ==========================

for rss in rss_feeds:

    try:

        feed = feedparser.parse(rss)

        print(f"\nChecking: {rss}")

        for item in feed.entries:

            if posted_today >= MAX_POSTS:
                break

            title = item.title.strip()

            if title in posted_news:
                continue

            if "summary" in item:
                summary = BeautifulSoup(
                    item.summary,
                    "html.parser"
                ).get_text()
            else:
                summary = "No summary available."

            summary = summary[:500]

            category = detect_category(title)

            message = f"""
{category}

📰 {title}

📌 Summary

{summary}

🔗 Source
{item.link}
"""

            response = requests.post(
                f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
                json={
                    "chat_id": CHAT_ID,
                    "text": message
                },
                timeout=20
            )

            if response.status_code == 200:

                print("Posted:", title)

                save_news(title)

                posted_news.add(title)

                posted_today += 1

            else:

                print("Failed:", title)

    except Exception as e:

        print("RSS Error:", rss)
        print(e)

print("Done!")
