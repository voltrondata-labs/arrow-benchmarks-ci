from distutils.version import StrictVersion
import requests

from config import Config
from integrations import adapter


class Pypi:
    def __init__(self):
        self.session = requests.Session()
        self.session.mount("https://", adapter)
        self.base_url = f"{Config.PIPY_API_BASE_URL}"

    def get_pyarrow_project(self):
        return self.session.get(
            f"{Config.PIPY_API_BASE_URL}/{Config.PIPY_PROJECT}/json"
        ).json()

    def get_pyarrow_versions_in_desc_order(self):
        project = self.get_pyarrow_project()
        version_numbers = list(
            filter(lambda x: "post" not in x, project["releases"].keys())
        )
        version_numbers.sort(reverse=True, key=StrictVersion)
        return version_numbers


pypi = Pypi()
