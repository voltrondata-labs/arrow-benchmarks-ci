from buildkite.schedule_and_publish.create_benchmark_builds import (
    create_benchmark_builds,
)
from buildkite.schedule_and_publish.get_commits import get_commits
from buildkite.schedule_and_publish.update_benchmark_builds_status import (
    update_benchmark_builds_status,
)
from models.machine import Machine
from models.run import Run


def test_update_benchmark_builds_status():
    get_commits()

    create_benchmark_builds()
    for machine in Machine.all():
        assert Run.first(machine_name=machine.name, status="scheduled")

    update_benchmark_builds_status()
    for machine in Machine.all():
        expected_status = "finished" if machine.name == "ursa-i9-9960x" else "failed"
        run = Run.first(machine_name=machine.name, status=expected_status)
        assert run
        assert run.finished_at
        assert run.total_run_time
