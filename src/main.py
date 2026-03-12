"""
保险资讯聚合推送系统 - 主程序
"""

import os
import sys
import logging
from datetime import datetime

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)


def send_wechat_message(webhook_url: str, content: str):
    """
    发送企业微信消息
    
    Args:
        webhook_url: 企业微信Webhook地址
        content: 消息内容（Markdown格式）
    
    Returns:
        bool: 是否发送成功
    """
    try:
        import requests
        
        data = {
            "msgtype": "markdown",
            "markdown": {
                "content": content
            }
        }
        
        response = requests.post(webhook_url, json=data, timeout=10)
        result = response.json()
        
        if result.get('errcode') == 0:
            logger.info("✅ 消息推送成功")
            return True
        else:
            logger.error(f"❌ 消息推送失败: {result}")
            return False
            
    except Exception as e:
        logger.error(f"❌ 消息推送异常: {e}")
        return False

def fetch_rss_news_v3():
    """
    中国保险行业资讯聚合 v3（增强央视网来源）
    """

    import feedparser
    from datetime import datetime, timedelta

    # ======================
    # RSS资讯源
    # ======================

    rss_sources = [

        # -------- 央视网 --------
        ("央视财经", "http://www.cctv.com/program/rss/02/04/index.xml", 1),
        ("央视经济", "http://www.cctv.com/program/rss/02/05/index.xml", 1),
        ("央视新闻", "http://www.cctv.com/program/rss/01/01/index.xml", 1),

        # -------- 政府 --------
        ("中国政府网", "http://www.gov.cn/rss/gwyw.xml", 1),

        # -------- 财经媒体 --------
        ("财新", "https://www.caixin.com/rss/finance.xml", 2),
        ("第一财经", "https://www.yicai.com/rss/news.xml", 2),
        ("财联社", "https://rsshub.app/cls/telegraph", 2),
        ("新浪财经", "https://finance.sina.com.cn/rss/finance.xml", 2),

        # -------- 保险社区 --------
        ("13个精算师", "https://rsshub.app/wechat/gh_7e0f706e6a79", 3),
        ("慧保天下", "https://rsshub.app/wechat/gh_ae3e6a1c2a9e", 3),

    ]

    # ======================
    # 保险关键词
    # ======================

    keywords = [

        "保险","险企","寿险","财险","再保险",

        "中国平安","中国人寿",
        "中国太保","中国人保",
        "新华保险","友邦保险",
        "泰康保险","阳光保险",

        "保险资金","保险投资",
        "保险监管","保险业"

    ]

    time_threshold = datetime.now() - timedelta(hours=24)

    raw_news = []

    # ======================
    # RSS抓取
    # ======================

    for source, url, priority in rss_sources:

        try:

            feed = feedparser.parse(url)

            for entry in feed.entries[:30]:

                title = entry.get("title", "")
                summary = entry.get("summary", "")
                link = entry.get("link", "")

                text = title + summary

                # 关键词过滤
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

    # ======================
    # 去重 + 热点统计
    # ======================

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

    # ======================
    # 排序逻辑
    # ======================

    news_list.sort(

        key=lambda x: (

            x["priority"],          # 官方优先
            -x["hot"],              # 热点
            x["time"] if x["time"] else datetime.min

        )

    )

    # ======================
    # 返回最多10条
    # ======================

    return news_list[:10]

def format_news_message(news_list):
    """
    格式化新闻消息
    
    Args:
        news_list: 新闻列表
    
    Returns:
        str: 格式化后的Markdown消息
    """
    today = datetime.now().strftime("%m.%d")
    
    message_lines = [
        f"## 📰 保险资讯早报",
        f"",
        f"> **日期**: {today}",
        f"> **来源**: 聚合多个权威渠道",
        f"",
    ]
    
    if not news_list:
        message_lines.extend([
            f"暂无新的保险资讯。",
            f"",
            f"系统将在明天继续为您推送。",
        ])
    else:
        for i, news in enumerate(news_list[:10], 1):  # 最多10条
            title = news.get('title', '无标题')
            link = news.get('link', '')
            summary = news.get('summary', '')
            
            message_lines.extend([
                f"**{i}. {title}**",
                f"> 来源: {news.get('source', '未知')}",
            ])
            
            if summary:
                message_lines.append(f"> 摘要: {summary}")
            
            if link:
                message_lines.append(f"> [查看详情]({link})")
            
            message_lines.append("")
    
    message_lines.extend([
        "---",
        f"*更新时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}*",
    ])
    
    return '\n'.join(message_lines)


def main():
    """主函数"""
    logger.info("="*60)
    logger.info("保险资讯聚合推送系统启动")
    logger.info("="*60)
    
    # 检查环境变量
    webhook = os.environ.get('WECHAT_WEBHOOK')
    
    if not webhook:
        logger.error("❌ 错误：未配置WECHAT_WEBHOOK环境变量")
        logger.error("请在GitHub Secrets中配置WECHAT_WEBHOOK")
        sys.exit(1)
    
    logger.info("✅ 已获取到企业微信Webhook配置")
    
    try:
        # 获取新闻
        logger.info("开始获取保险资讯...")
        news_list = fetch_rss_news()
        
        # 格式化消息
        logger.info("格式化消息...")
        message = format_news_message(news_list)
        
        # 推送消息
        logger.info("推送消息到企业微信...")
        success = send_wechat_message(webhook, message)
        
        if success:
            logger.info("✅ 推送完成")
        else:
            logger.error("❌ 推送失败")
            sys.exit(1)
        
    except Exception as e:
        logger.error(f"❌ 程序执行失败: {e}")
        # 即使失败也推送错误消息
        error_message = f"""## ❌ 系统错误

推送过程中发生错误：{str(e)}

请联系管理员处理。

---
*时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}*"""
        send_wechat_message(webhook, error_message)
        sys.exit(1)
    
    logger.info("="*60)
    logger.info("任务完成")
    logger.info("="*60)


if __name__ == "__main__":
    main()
