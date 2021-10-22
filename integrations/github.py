import requests

from config import Config
from integrations import adapter


class Github:
    def __init__(self):
        self.session = requests.Session()
        self.session.mount("https://", adapter)
        if Config.GITHUB_API_TOKEN:
            self.session.headers = {
                "Authorization": f"Bearer {Config.GITHUB_API_TOKEN}"
            }
        self.base_url = f"{Config.GITHUB_API_BASE_URL}/repos/{Config.GITHUB_REPO_WITH_BENCHMARKABLE_COMMITS}"

    def get_commits(self):
        return self.session.get(
            f"{self.base_url}/commits?per_page={Config.MAX_COMMITS_TO_FETCH}"
        ).json()


github = Github()
