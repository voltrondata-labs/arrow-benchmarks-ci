import pytest

from app import app
from buildkite.deploy.update_machine_configs import update_machine_configs
from db import Session
from tests.helpers import delete_data, machine_configs, mock_offline_machine


@pytest.fixture(autouse=True)
def run_before_and_after_tests():
    delete_data()
    update_machine_configs(machine_configs)
    mock_offline_machine()
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
