import os
import requests
from datetime import datetime

def main():
    """主函数"""
    print("="*60)
    print("保险资讯聚合推送系统启动")
    print("="*60)
    
    webhook = os.environ.get('WECHAT_WEBHOOK')
    
    if not webhook:
        print("错误：未配置WECHAT_WEBHOOK环境变量")
        return
    
    today = datetime.now().strftime("%m.%d")
    
    message = f"""## 📰 保险资讯早报

> **日期**: {today}
> **来源**: 聚合多个权威渠道

✅ 系统部署成功！

明天早上8:30将自动推送保险资讯到企业微信群。

**数据来源：**
- 央视网财经新闻
- 国家金融监督管理总局
- 中国保险行业协会
- 中国银行保险报
- 13个精算师

---
*更新时间：{datetime.now().strftime('%Y-%m-%d %H:%M')}*"""

    data = {
        "msgtype": "markdown",
        "markdown": {
            "content": message
        }
    }
    
    try:
        response = requests.post(webhook, json=data)
        result = response.json()
        
        if result.get('errcode') == 0:
            print("✅ 推送成功！")
        else:
            print(f"❌ 推送失败: {result}")
            
    except Exception as e:
        print(f"❌ 推送异常: {e}")

if __name__ == "__main__":
    main()
