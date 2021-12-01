import json

from buildkite.schedule_and_publish.get_commits import get_commits
from models.machine import Machine
from models.run import Run

run_context = {
    "context": {"1": "2"},
    "machine_info": {"2": "3"},
    "conda_packages": "conda packages...",
}


def update_run(client, run_id=None, api_access_token=None):
    get_commits()

    if not run_id:
        run = Run.first()
        run_id = run.id
        assert not run.context
        assert not run.machine_info
        assert not run.conda_packages

    if not api_access_token:
        run = Run.get(run_id)
        api_access_token = run.machine.create_api_access_token()

    return run_id, client.post(
        f"/runs/{run_id}",
        data=json.dumps(run_context),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_access_token}",
        },
    )


def test_runs_201(client):
    run_id, response = update_run(client)
    assert response.status_code == 201

    run = Run.get(run_id)
    assert run.context == run_context["context"]
    assert run.machine_info == run_context["machine_info"]
    assert run.conda_packages == run_context["conda_packages"]


def test_runs_401_invalid_token(client):
    run_id, response = update_run(client, run_id=None, api_access_token="invalid token")
    assert response.status_code == 401

    run = Run.get(run_id)
    assert not run.context
    assert not run.machine_info
    assert not run.conda_packages


def test_runs_404_unknown_run(client):
    api_access_token = Machine.first().create_api_access_token()
    run_id, response = update_run(
        client, run_id="unknown", api_access_token=api_access_token
    )
    assert response.status_code == 404
