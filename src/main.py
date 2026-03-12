"""
保险资讯聚合推送系统 - 主程序
"""

import os
import sys
import logging
from datetime import datetime
from rss_fetcher import fetch_rss_news_v3

# 日志配置
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)

logger = logging.getLogger(__name__)


def send_wechat_message(webhook_url: str, content: str):

    try:
        import requests

        data = {
            "msgtype": "markdown",
            "markdown": {"content": content}
        }

        response = requests.post(webhook_url, json=data, timeout=10)
        result = response.json()

        if result.get("errcode") == 0:
            logger.info("✅ 消息推送成功")
            return True
        else:
            logger.error(f"❌ 消息推送失败: {result}")
            return False

    except Exception as e:
        logger.error(f"❌ 推送异常: {e}")
        return False


def format_news_message(news_list):

    today = datetime.now().strftime("%m.%d")

    message = [
        "## 📰 保险资讯早报",
        "",
        f"> **日期**: {today}",
        "> **来源**: 央视 / 财联社 / 财新 / 第一财经等",
        ""
    ]

    if not news_list:

        message.append("暂无新的保险资讯。")

    else:

        for i, news in enumerate(news_list[:10], 1):

            title = news.get("title", "")
            link = news.get("link", "")
            summary = news.get("summary", "")
            source = news.get("source", "")

            message.append(f"**{i}. {title}**")
            message.append(f"> 来源: {source}")

            if summary:
                message.append(f"> 摘要: {summary}")

            if link:
                message.append(f"> [查看详情]({link})")

            message.append("")

    message.append("---")
    message.append(f"*更新时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}*")

    return "\n".join(message)


def main():

    logger.info("====== 保险资讯系统启动 ======")

    webhook = os.environ.get("WECHAT_WEBHOOK")

    if not webhook:

        logger.error("未配置 WECHAT_WEBHOOK")
        sys.exit(1)

    try:

        logger.info("抓取新闻...")

        news_list = fetch_rss_news_v3()

        logger.info(f"获取 {len(news_list)} 条新闻")

        message = format_news_message(news_list)

        logger.info("推送企业微信...")

        success = send_wechat_message(webhook, message)

        if not success:
            sys.exit(1)

    except Exception as e:

        logger.error(f"程序异常: {e}")

        error_msg = f"""## ❌ 系统错误

推送过程中发生错误：

{str(e)}

---
{datetime.now().strftime('%Y-%m-%d %H:%M')}
"""

        send_wechat_message(webhook, error_msg)

        sys.exit(1)

    logger.info("任务完成")


if __name__ == "__main__":
    main()
