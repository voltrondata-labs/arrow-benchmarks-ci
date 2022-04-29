from buildkite.schedule_and_publish.create_benchmark_builds import (
    create_benchmark_builds,
)
from buildkite.schedule_and_publish.get_commits import get_commits
from models.run import Run
from tests.helpers import machine_configs


def test_create_benchmark_builds_no_pull_requests():
    get_commits()

    assert not Run.all(status="scheduled")

    # machine.scheduled_or_running_builds() = [] for unit tests
    create_benchmark_builds()
    for machine_name, params in machine_configs.items():
        runs = Run.all(machine_name=machine_name, status="scheduled")
        assert len(runs) == params["max_builds"]
        for run in runs:
            assert run.scheduled_at
