import requests
from bs4 import BeautifulSoup
import json
import os
from openai import OpenAI
import time
import re

# 配置 OpenAI API 密钥
client = OpenAI()

# 企业微信 Webhook 地址
WECOM_WEBHOOK_URL = os.environ.get("WECOM_WEBHOOK_URL")

def fetch_url(url, retries=3, delay=5):
    """带重试机制的 URL 请求函数"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    for i in range(retries):
        try:
            response = requests.get(url, headers=headers, timeout=20, verify=False) # 增加超时时间并禁用SSL证书验证
            response.raise_for_status()
            return response
        except requests.exceptions.SSLError as e:
            print(f"SSL Error fetching {url}: {e}. Retrying in {delay} seconds...")
            time.sleep(delay)
        except requests.exceptions.RequestException as e:
            print(f"Request Error fetching {url}: {e}. Retrying in {delay} seconds...")
            time.sleep(delay)
    print(f"Failed to fetch {url} after {retries} retries.")
    return None

def get_stcn_news():
    """从证券时报网站抓取新闻"""
    print("Starting to fetch news from STCN...")
    news_urls = [
        "https://www.stcn.com/article/detail/3377901.html",
        "https://www.stcn.com/article/detail/3658242.html",
        "https://www.stcn.com/article/detail/3558952.html",
        "https://www.stcn.com/article/detail/3662753.html",
        "https://www.stcn.com/article/detail/3662147.html",
        "https://www.stcn.com/article/detail/3652553.html",
        "https://stcn.com/article/detail/1564481.html",
        "https://www.stcn.com/article/detail/3658228.html",
        "https://www.stcn.com/article/detail/3658095.html",
        "https://stcn.com/article/detail/1476734.html"
    ]
    all_news = []

    for url in news_urls:
        response = fetch_url(url)
        if response:
            soup = BeautifulSoup(response.text, 'html.parser')
            # 证券时报的标题在 <div class="detail-title"> 内部
            title_div = soup.find('div', class_='detail-title')
            title = title_div.get_text(strip=True) if title_div else "No Title Found"
            all_news.append({'title': title, 'link': url, 'source': '证券时报'})
            print(f"Fetched title: {title} from {url}")
    print(f"Finished fetching {len(all_news)} news items from STCN.")
    return all_news

def summarize_text(text):
    """使用 OpenAI API 提取文本摘要"""
    print("Starting text summarization with OpenAI...")
    if not text or len(text.strip()) < 50: # 如果文本太短，直接返回
        print("Text too short for summarization.")
        return text.strip()
    try:
        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                {"role": "system", "content": "你是一个专业的摘要提取助手，请用中文简洁地概括以下文章的主要内容，限制在100字以内。"},
                {"role": "user", "content": text[:2000] # 限制输入长度以避免超长
                }
            ],
            max_tokens=150
        )
        summary = response.choices[0].message.content.strip()
        print("Text summarization completed.")
        return summary
    except Exception as e:
        print(f"Error summarizing text with OpenAI: {e}")
        return "[摘要生成失败]"

def get_article_content(url):
    """获取文章正文内容"""
    print(f"Starting to fetch article content for {url}...")
    response = fetch_url(url)
    if not response:
        print(f"Failed to fetch article content for {url}.")
        return ""

    soup = BeautifulSoup(response.text, 'html.parser')
    # 证券时报的文章内容在 <div class="detail-content"> 中
    content_div = soup.find('div', class_='detail-content')
    
    if content_div:
        content = content_div.get_text(separator='\n', strip=True)
        print(f"Fetched article content for {url}.")
        return content
    print(f"Could not find content div for {url}.")
    return ""

def send_to_wecom(news_items):
    """将新闻发送到企业微信群"""
    print("Starting to send news to WeChat Work...")
    if not WECOM_WEBHOOK_URL:
        print("WECOM_WEBHOOK_URL is not set. Skipping WeChat Work notification.")
        return
    if not news_items:
        print("No news to send.")
        return

    messages = []
    for item in news_items:
        messages.append(f">**标题**: {item['title']}\n>**摘要**: {item['summary']}\n>**来源**: {item['source']}\n>[阅读原文]({item['link']})")
    
    markdown_text = "## 每日保险热点资讯\n" + "\n\n---\n\n".join(messages)

    data = {
        "msgtype": "markdown",
        "markdown": {
            "content": markdown_text
        }
    }
    headers = {'Content-Type': 'application/json'}

    try:
        response = requests.post(WECOM_WEBHOOK_URL, headers=headers, data=json.dumps(data), timeout=10)
        response.raise_for_status()
        result = response.json()
        if result.get('errcode') == 0:
            print("News successfully sent to WeChat Work.")
        else:
            print(f"Failed to send news to WeChat Work: {result.get('errmsg')}")
    except requests.exceptions.RequestException as e:
        print(f"Error sending news to WeChat Work: {e}")
    print("Finished sending news to WeChat Work.")

def main():
    print("Main function started.")
    all_news = []

    all_news.extend(get_stcn_news())

    # 去重
    unique_news = {item['link']: item for item in all_news}.values()

    hot_news = []
    for news in list(unique_news)[:10]: # 控制在10条以内
        print(f"Processing news: {news['title']}")
        article_content = get_article_content(news['link'])
        if article_content:
            summary = summarize_text(article_content)
            news['summary'] = summary
        else:
            news['summary'] = "[无法获取文章内容]"
        hot_news.append(news)
        print(f"Finished processing news: {news['title']}")

    send_to_wecom(hot_news)
    print("Main function finished.")

if __name__ == "__main__":
    # 在运行前禁用requests的InsecureRequestWarning
    requests.packages.urllib3.disable_warnings(requests.packages.urllib3.exceptions.InsecureRequestWarning)
    main()
