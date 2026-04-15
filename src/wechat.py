import requests


def send(webhook, content):

    data = {
        "msgtype": "markdown",
        "markdown": {"content": content}
    }

    requests.post(webhook, json=data)
