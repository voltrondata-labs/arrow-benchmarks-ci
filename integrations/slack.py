import json

import requests

from config import Config
from integrations import adapter


class Slack:
    def __init__(self):
        self.session = requests.Session()
        self.session.mount("https://", adapter)
        self.session.headers = {
            "Authorization": f"Bearer {Config.SLACK_API_TOKEN}",
            "Content-Type": "application/json",
        }
        self.base_url = Config.SLACK_API_BASE_URL
        self.slack_channel = Config.SLACK_CHANNEL_FOR_BENCHMARK_RESULTS

    def post_message(self, text):
        data = {"channel": self.slack_channel, "text": text}
        return self.session.post(
            f"{self.base_url}/chat.postMessage", data=json.dumps(data)
        ).json()


slack = Slack()
