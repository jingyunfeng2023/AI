import os
import requests
from datetime import datetime

def main():
    webhook = os.environ.get('WECHAT_WEBHOOK')
    if not webhook:
        print("错误：未配置WECHAT_WEBHOOK")
        return

    today = datetime.now().strftime("%m.%d")
    message = f"""## 📰 保险资讯早报

> **日期**: {today}
> **状态**: 测试推送

系统部署成功！明天早上8:30将自动推送保险资讯。

---
*更新时间：{datetime.now().strftime('%Y-%m-%d %H:%M')}*"""

    data = {
        "msgtype": "markdown",
        "markdown": {"content": message}
    }

    response = requests.post(webhook, json=data)
    print(f"推送结果: {response.json()}")

if __name__ == "__main__":
    main()
