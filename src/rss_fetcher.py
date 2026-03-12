"""
中国保险资讯RSS聚合模块
"""

import feedparser
from datetime import datetime, timedelta


def fetch_rss_news(hours_limit=24):

    rss_sources = [

        # 官方
        ("央视财经", "http://www.cctv.com/program/rss/02/04/index.xml", 1),
        ("央视新闻", "http://www.cctv.com/program/rss/01/01/index.xml", 1),
        ("中国政府网", "http://www.gov.cn/rss/gwyw.xml", 1),

        # 财经媒体
        ("财联社", "https://rsshub.app/cls/telegraph", 2),
        ("财新", "https://www.caixin.com/rss/finance.xml", 2),
        ("第一财经", "https://www.yicai.com/rss/news.xml", 2),

        # 保险社区
        ("13个精算师", "https://rsshub.app/wechat/gh_7e0f706e6a79", 3),
        ("慧保天下", "https://rsshub.app/wechat/gh_ae3e6a1c2a9e", 3),

    ]

    keywords = [

        "保险","险企","寿险","财险","再保险",

        "中国平安","中国人寿",
        "中国太保","中国人保",
        "新华保险","友邦保险",
        "泰康保险","阳光保险",

        "保险资金","保险投资",
        "保险监管","保险业"
    ]

    time_threshold = datetime.now() - timedelta(hours=hours_limit)

    raw_news = []

    for source, url, priority in rss_sources:

        try:

            feed = feedparser.parse(url)

            for entry in feed.entries[:30]:

                title = entry.get("title", "")
                summary = entry.get("summary", "")
                link = entry.get("link", "")

                text = title + summary

                if not any(k in text for k in keywords):
                    continue

                published_time = None

                if hasattr(entry, "published_parsed") and entry.published_parsed:
                    published_time = datetime(*entry.published_parsed[:6])

                if published_time and published_time < time_threshold:
                    continue

                raw_news.append({

                    "title": title.strip(),
                    "summary": summary[:120],
                    "link": link,
                    "source": source,
                    "priority": priority,
                    "time": published_time

                })

        except Exception as e:

            print("RSS抓取失败:", source, e)

    # 去重 + 热点统计
    news_map = {}

    for item in raw_news:

        title = item["title"]

        if title not in news_map:

            news_map[title] = item
            news_map[title]["hot"] = 1

        else:

            news_map[title]["hot"] += 1

            if item["priority"] < news_map[title]["priority"]:

                news_map[title]["source"] = item["source"]
                news_map[title]["priority"] = item["priority"]

    news_list = list(news_map.values())

    # 排序
    news_list.sort(

        key=lambda x: (

            x["priority"],
            -x["hot"],
            x["time"] if x["time"] else datetime.min

        )

    )

    return news_list[:10]
