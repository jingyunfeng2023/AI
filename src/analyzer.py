def analyze_news(news_list):

    hot_map = {}

    for n in news_list:

        t = n["title"]

        if t not in hot_map:
            hot_map[t] = n
            hot_map[t]["count"] = 1
        else:
            hot_map[t]["count"] += 1

    result = list(hot_map.values())

    # 热点排序
    result.sort(key=lambda x: (-x["count"], x["priority"]))

    return result[:15]


def policy_impact(text):

    impact = []

    if "降息" in text or "宽松" in text:
        impact.append("利好股市")

    if "监管" in text or "收紧" in text:
        impact.append("利空高风险资产")

    if "新能源" in text:
        impact.append("利好新能源板块")

    if "房地产" in text:
        impact.append("影响地产链")

    return " / ".join(impact) if impact else "市场中性"


def market_summary(news_list):

    summary = []

    texts = " ".join([n["title"] for n in news_list])

    if "监管" in texts:
        summary.append("监管趋严")

    if "利率" in texts:
        summary.append("利率变化")

    if "资金" in texts:
        summary.append("流动性波动")

    if not summary:
        summary.append("市场平稳")

    return "、".join(summary)
