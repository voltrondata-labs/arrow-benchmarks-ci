import requests

from config import Config
from integrations import adapter


class ConbenchException(Exception):
    pass


class ConbenchNotFoundException(Exception):
    pass


class Conbench:
    def __init__(self):
        self.session = requests.Session()
        self.session.mount("https://", adapter)
        self.session.mount("http://", adapter)
        self.session.headers = {"Content-Type": "application/json"}
        self.base_url = f"{Config.CONBENCH_URL}/api"

    def get_compare_runs(self, baseline_run_id, contender_run_id):
        url = f"{self.base_url}/compare/runs/{baseline_run_id}...{contender_run_id}/"
        response = self.session.get(url)

        if response.status_code == 404:
            raise ConbenchNotFoundException(
                f"{url} {response.status_code} {response.json()}"
            )

        if response.status_code > 399:
            raise ConbenchException(f"{url} {response.status_code} {response.content}")

        return response.json()


conbench = Conbench()
