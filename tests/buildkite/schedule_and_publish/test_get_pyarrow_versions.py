from buildkite.schedule_and_publish.get_pyarrow_versions import get_pyarrow_versions
from models.benchalerts_run import BenchalertsRun
from models.benchmarkable import Benchmarkable
from models.machine import Machine
from models.run import Run


def verify_benchmarkable(version, prev_version):
    benchmarkable = Benchmarkable.get(f"pyarrow=={version}")
    assert benchmarkable
    assert benchmarkable.type == "pyarrow-apache-wheel"
    assert benchmarkable.reason == "pyarrow-apache-wheel"
    assert not benchmarkable.data
    assert not benchmarkable.pull_number
    if prev_version:
        assert benchmarkable.baseline_id == f"pyarrow=={prev_version}"
    else:
        assert not benchmarkable.baseline_id


def verify_benchmarkable_runs(version):
    benchmarkable_id = f"pyarrow=={version}"
    for machine in [
        m for m in Machine.all() if m.default_filters.get("pyarrow-apache-wheel")
    ]:
        run = Run.first(benchmarkable_id=benchmarkable_id, machine_name=machine.name)
        assert run
        assert run.filters == machine.default_filters["pyarrow-apache-wheel"]
        assert run.reason == "pyarrow-apache-wheel"
        assert run.status == "created"
        assert not run.finished_at


def verify_benchmarkable_benchalerts_runs(version):
    benchmarkable_id = f"pyarrow=={version}"
    benchalerts_run = BenchalertsRun.first(benchmarkable_id=benchmarkable_id)
    assert benchalerts_run is None


def test_get_pyarrow_versions():
    get_pyarrow_versions()

    for version, prev_version in [("5.0.0", "4.0.1"), ("4.0.1", None)]:
        verify_benchmarkable(version, prev_version)
        verify_benchmarkable_runs(version)
        verify_benchmarkable_benchalerts_runs(version)
