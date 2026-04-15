import os
from datetime import datetime

from rss_fetcher import fetch_rss_news
from analyzer import analyze_news, policy_impact, market_summary
from wechat import send


def format_message(news):

    today = datetime.now().strftime("%m.%d")

    msg = f"## 📊 金融情报早报\n\n日期：{today}\n\n"

    # 市场总结
    msg += f"### 📌 今日核心逻辑\n"
    msg += f"> {market_summary(news)}\n\n"

    msg += "### 🔥 热点资讯\n\n"

    for i, n in enumerate(news, 1):

        msg += f"**{i}. {n['title']}**\n"
        msg += f"> 来源：{n['source']}\n"

        impact = policy_impact(n["title"])

        msg += f"> 影响：{impact}\n"

        if n["link"]:
            msg += f"> [查看详情]({n['link']})\n"

        msg += "\n"

    msg += "---\n"
    msg += f"*更新时间：{datetime.now()}*"

    return msg


def main():

    webhook = os.getenv("WECHAT_WEBHOOK")

    news = fetch_rss_news()

    analyzed = analyze_news(news)

    msg = format_message(analyzed)

    send(webhook, msg)


if __name__ == "__main__":
    main()
