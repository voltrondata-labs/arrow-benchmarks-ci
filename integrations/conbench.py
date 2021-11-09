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
        # TODO: Remove this
        url = f"{self.base_url}/compare/runs/31971634-7204-4fa5-a16e-f4f1154a57e2...77cb3ad6-c6fb-4c8d-815d-6c66a63ac9ee/"

        response = self.session.get(url)

        if response.status_code == 404:
            raise ConbenchNotFoundException(
                f"{url} {response.status_code} {response.json()}"
            )

        if response.status_code > 399:
            raise ConbenchException(f"{url} {response.status_code} {response.content}")

        return response.json()


conbench = Conbench()
