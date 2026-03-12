"""
保险资讯自动推送系统
"""

import os
import sys
import logging
import requests
from datetime import datetime

from rss_fetcher import fetch_rss_news


logging.basicConfig(

    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"

)

logger = logging.getLogger(__name__)


def send_wechat(webhook, content):

    data = {

        "msgtype": "markdown",

        "markdown": {
            "content": content
        }

    }

    r = requests.post(webhook, json=data)

    return r.json()


def format_news(news_list):

    today = datetime.now().strftime("%m.%d")

    lines = [

        "## 📰 保险资讯早报",
        "",
        f"> 日期：{today}",
        "> 来源：央视 / 财联社 / 财新 / 第一财经",
        ""
    ]

    if not news_list:

        lines.append("暂无新的保险资讯")

    else:

        for i, n in enumerate(news_list, 1):

            lines.append(f"**{i}. {n['title']}**")
            lines.append(f"> 来源：{n['source']}")

            if n["summary"]:
                lines.append(f"> 摘要：{n['summary']}")

            if n["link"]:
                lines.append(f"> [查看详情]({n['link']})")

            lines.append("")

    lines.append("---")
    lines.append(f"*更新时间：{datetime.now().strftime('%Y-%m-%d %H:%M')}*")

    return "\n".join(lines)


def main():

    webhook = os.getenv("WECHAT_WEBHOOK")

    if not webhook:

        logger.error("未配置 WECHAT_WEBHOOK")
        sys.exit(1)

    logger.info("抓取新闻")

    news = fetch_rss_news()

    logger.info(f"获取 {len(news)} 条新闻")

    message = format_news(news)

    logger.info("推送企业微信")

    send_wechat(webhook, message)


if __name__ == "__main__":
    main()
