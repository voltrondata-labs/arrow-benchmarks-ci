import os
import pytest

from app import app
from config import Config
from buildkite.deploy.update_machine_configs import update_machine_configs
from db import Session
from tests.helpers import delete_data, machine_configs, mock_offline_machine


@pytest.fixture(autouse=True)
def run_before_and_after_tests():
    delete_data()
    update_machine_configs(machine_configs)
    mock_offline_machine()
    Config.GITHUB_REPOS_WITH_BENCHMARKABLE_COMMITS = {
        "apache/arrow": {
            "benchmarkable_type": "arrow-commit",
            "enable_benchmarking_for_pull_requests": True,
            "github_secret": os.getenv("GITHUB_SECRET"),
            "publish_benchmark_results_on_pull_requests": True,
        }
    }
    yield


@pytest.fixture
def application():
    with app.app_context():
        pass

    yield app

    with app.app_context():
        Session.remove()


@pytest.fixture
def client(application):
    return application.test_client()
