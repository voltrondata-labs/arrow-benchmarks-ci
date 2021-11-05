from buildkite.schedule_and_publish.create_benchmark_builds import \
    create_benchmark_builds
from buildkite.schedule_and_publish.get_commits import get_commits
from buildkite.schedule_and_publish.update_benchmark_builds_status import \
    update_benchmark_builds_status
from models.run import Run


def test_update_benchmark_builds_status():
    get_commits()

    create_benchmark_builds()
    assert Run.first(machine_name="ursa-i9-9960x", status="scheduled")
    assert Run.first(machine_name="ursa-thinkcentre-m75q", status="scheduled")

    update_benchmark_builds_status()
    run1 = Run.first(machine_name="ursa-i9-9960x", status="finished")
    run2 = Run.first(machine_name="ursa-thinkcentre-m75q", status="failed")

    for run in [run1, run2]:
        assert run
        assert run.finished_at
        assert run.total_run_time
