import json
import os

from buildkite.schedule_and_publish.get_commits import get_commits
from config import Config
from models.benchalerts_run import BenchalertsRun
from models.benchmarkable import Benchmarkable
from models.machine import Machine
from models.run import Run

commit_dicts = json.load(open("tests/mocked_integrations/github/get_commits.json"))


def verify_benchmarkable(commit_dict):
    benchmarkable = Benchmarkable.get(commit_dict["sha"])
    assert benchmarkable
    assert benchmarkable.type == "arrow-commit"
    assert benchmarkable.data == commit_dict
    assert benchmarkable.baseline_id == commit_dict["parents"][-1]["sha"]
    assert benchmarkable.reason == "arrow-commit"
    assert benchmarkable.pull_number == 10973


def verify_benchmarkable_runs(commit_dict):
    benchmarkable_id = commit_dict["sha"]
    for machine in Machine.all():
        run = Run.first(benchmarkable_id=benchmarkable_id, machine_name=machine.name)
        assert run
        assert run.filters == machine.default_filters["arrow-commit"]
        assert run.reason == "arrow-commit"
        assert run.status == "created"
        assert not run.finished_at


def verify_benchmarkable_benchalerts_runs(
    commit_dict, publish_benchmark_results_on_pull_requests=True
):
    benchmarkable_id = commit_dict["sha"]
    if publish_benchmark_results_on_pull_requests:
        assert BenchalertsRun.first(benchmarkable_id=benchmarkable_id)
    else:
        assert BenchalertsRun.first(benchmarkable_id=benchmarkable_id) is None


def test_get_commits():
    get_commits()

    for commit_dict in commit_dicts:
        verify_benchmarkable(commit_dict)
        verify_benchmarkable_runs(commit_dict)
        verify_benchmarkable_benchalerts_runs(commit_dict)


def test_get_commits_with_publish_benchmark_results_on_pull_requests_off():
    Config.GITHUB_REPOS_WITH_BENCHMARKABLE_COMMITS = {
        "apache/arrow": {
            "benchmarkable_type": "arrow-commit",
            "enable_benchmarking_for_pull_requests": True,
            "github_secret": os.getenv("GITHUB_SECRET"),
            "publish_benchmark_results_on_pull_requests": False,
        }
    }
    get_commits()

    for commit_dict in commit_dicts:
        verify_benchmarkable(commit_dict)
        verify_benchmarkable_runs(commit_dict)
        verify_benchmarkable_benchalerts_runs(
            commit_dict, publish_benchmark_results_on_pull_requests=False
        )
