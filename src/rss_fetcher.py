import feedparser
from datetime import datetime, timedelta


def fetch_rss_news(hours_limit=24):

    sources = [

        # 监管
        ("中国政府网", "http://www.gov.cn/rss/gwyw.xml", 1),

        # 国内媒体
        ("财联社", "https://rsshub.app/cls/telegraph", 2),
        ("第一财经", "https://www.yicai.com/rss/news.xml", 2),

        # 国际
        ("Reuters", "https://feeds.reuters.com/reuters/businessNews", 2),
        ("Bloomberg", "https://feeds.bloomberg.com/markets/news.rss", 2),

    ]

    keywords = [
        "政策","监管","经济","市场","融资",
        "A股","港股","利率","资金","IPO"
    ]

    time_limit = datetime.now() - timedelta(hours=hours_limit)

    news = []

    for name, url, priority in sources:

        try:
            feed = feedparser.parse(url)

            for e in feed.entries[:30]:

                text = e.get("title","") + e.get("summary","")

                if not any(k.lower() in text.lower() for k in keywords):
                    continue

                news.append({
                    "title": e.get("title"),
                    "summary": e.get("summary","")[:100],
                    "link": e.get("link"),
                    "source": name,
                    "priority": priority,
                })

        except:
            pass

    return news
