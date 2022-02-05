import json

import requests

from config import Config
from integrations import adapter
from logger import log


class Github:
    def __init__(self, repo):
        self.session = requests.Session()
        self.session.mount("https://", adapter)
        self.session.mount("http://", adapter)
        if Config.GITHUB_API_TOKEN:
            self.session.headers = {
                "Authorization": f"Bearer {Config.GITHUB_API_TOKEN}"
            }
        self.base_url = f"{Config.GITHUB_API_BASE_URL}/repos/{repo}"

    def get_commits(self):
        return self.session.get(
            f"{self.base_url}/commits?per_page={Config.MAX_COMMITS_TO_FETCH}"
        ).json()

    def get_commit(self, sha):
        return self.session.get(f"{self.base_url}/commits/{sha}").json()

    def get_pull(self, pull_number):
        return self.session.get(f"{self.base_url}/pulls/{pull_number}").json()

    def create_pull_comment(self, pull_number, comment_body):
        data = {"body": comment_body}
        return self.session.post(
            f"{self.base_url}/issues/{pull_number}/comments", data=json.dumps(data)
        ).json()

    def update_pull_comment(self, url, comment_body):
        data = {"body": comment_body}
        log.info(f"Updating {url}")
        return self.session.patch(url, data=json.dumps(data)).json()
