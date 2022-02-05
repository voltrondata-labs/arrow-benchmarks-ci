import json

from api.events import benchmark_command_examples
from buildkite.deploy.update_machine_configs import update_machine_configs
from config import Config
from models.benchmarkable import Benchmarkable
from models.machine import Machine
from models.run import Run
from tests.helpers import (
    delete_data,
    filter_with_cpp_only_benchmarks,
    filter_with_java_script_only_benchmarks,
    filter_with_python_only_benchmarks,
    filter_with_r_only_benchmarks,
    filter_with_file_write_only_benchmarks,
    filter_with_file_write_python_only_benchmarks,
    filter_with_file_only_benchmarks,
    machine_configs,
    make_github_webhook_event_for_comment,
    mock_offline_machine,
    outbound_requests,
    test_baseline_benchmarkable_id,
    test_benchmarkable_id,
    test_pull_number,
)

pull_comments_with_expected_machine_run_filters_and_skip_reason = {
    "@ursabot please benchmark lang=Python": {
        "ursa-i9-9960x": (filter_with_python_only_benchmarks, None),
        "ursa-thinkcentre-m75q": (
            {"lang": "Python"},
            "Only ['C++', 'Java'] langs are supported on ursa-thinkcentre-m75q",
        ),
        "new-machine": (
            {"lang": "Python"},
            "Only ['C++', 'Java'] langs are supported on new-machine",
        ),
    },
    "@ursabot please benchmark": {
        "ursa-i9-9960x": (
            machine_configs["ursa-i9-9960x"]["default_filters"]["arrow-commit"],
            None,
        ),
        "ursa-thinkcentre-m75q": (
            machine_configs["ursa-thinkcentre-m75q"]["default_filters"]["arrow-commit"],
            None,
        ),
        "new-machine": (
            machine_configs["new-machine"]["default_filters"]["arrow-commit"],
            None,
        ),
    },
    "@ursabot please benchmark    ": {
        "ursa-i9-9960x": (
            machine_configs["ursa-i9-9960x"]["default_filters"]["arrow-commit"],
            None,
        ),
        "ursa-thinkcentre-m75q": (
            machine_configs["ursa-thinkcentre-m75q"]["default_filters"]["arrow-commit"],
            None,
        ),
        "new-machine": (
            machine_configs["new-machine"]["default_filters"]["arrow-commit"],
            None,
        ),
    },
    "@ursabot please benchmark lang=Python   ": {
        "ursa-i9-9960x": (filter_with_python_only_benchmarks, None),
        "ursa-thinkcentre-m75q": (
            {"lang": "Python"},
            "Only ['C++', 'Java'] langs are supported on ursa-thinkcentre-m75q",
        ),
        "new-machine": (
            {"lang": "Python"},
            "Only ['C++', 'Java'] langs are supported on new-machine",
        ),
    },
    "@ursabot please benchmark lang=JavaScript   ": {
        "ursa-i9-9960x": (filter_with_java_script_only_benchmarks, None),
        "ursa-thinkcentre-m75q": (
            {"lang": "JavaScript"},
            "Only ['C++', 'Java'] langs are supported on ursa-thinkcentre-m75q",
        ),
        "new-machine": (
            {"lang": "JavaScript"},
            "Only ['C++', 'Java'] langs are supported on new-machine",
        ),
    },
    "@ursabot please benchmark lang=C++": {
        "ursa-i9-9960x": (
            {"lang": "C++"},
            "Only ['JavaScript', 'Python', 'R'] langs are supported on ursa-i9-9960x",
        ),
        "ursa-thinkcentre-m75q": (filter_with_cpp_only_benchmarks, None),
        "new-machine": (filter_with_cpp_only_benchmarks, None),
    },
    "\r\n@ursabot please benchmark   lang=C++": {
        "ursa-i9-9960x": (
            {"lang": "C++"},
            "Only ['JavaScript', 'Python', 'R'] langs are supported on ursa-i9-9960x",
        ),
        "ursa-thinkcentre-m75q": (filter_with_cpp_only_benchmarks, None),
        "new-machine": (filter_with_cpp_only_benchmarks, None),
    },
    "@ursabot please benchmark lang=R": {
        "ursa-i9-9960x": (filter_with_r_only_benchmarks, None),
        "ursa-thinkcentre-m75q": (
            {"lang": "R"},
            "Only ['C++', 'Java'] langs are supported on ursa-thinkcentre-m75q",
        ),
        "new-machine": (
            {"lang": "R"},
            "Only ['C++', 'Java'] langs are supported on new-machine",
        ),
    },
    "@ursabot please benchmark name=file-write": {
        "ursa-i9-9960x": (filter_with_file_write_only_benchmarks, None),
        "ursa-thinkcentre-m75q": (
            {"name": "file-write"},
            "Only ['lang', 'command'] filters are supported on ursa-thinkcentre-m75q",
        ),
        "new-machine": (
            {"name": "file-write"},
            "Only ['lang', 'command'] filters are supported on new-machine",
        ),
    },
    "@ursabot please benchmark name=file-write lang=Python": {
        "ursa-i9-9960x": (filter_with_file_write_python_only_benchmarks, None),
        "ursa-thinkcentre-m75q": (
            {"lang": "Python", "name": "file-write"},
            "Only ['C++', 'Java'] langs are supported on ursa-thinkcentre-m75q",
        ),
        "new-machine": (
            {"lang": "Python", "name": "file-write"},
            "Only ['C++', 'Java'] langs are supported on new-machine",
        ),
    },
    "@ursabot please benchmark    name=file-write  lang=Python ": {
        "ursa-i9-9960x": (filter_with_file_write_python_only_benchmarks, None),
        "ursa-thinkcentre-m75q": (
            {"lang": "Python", "name": "file-write"},
            "Only ['C++', 'Java'] langs are supported on ursa-thinkcentre-m75q",
        ),
        "new-machine": (
            {"lang": "Python", "name": "file-write"},
            "Only ['C++', 'Java'] langs are supported on new-machine",
        ),
    },
    "@ursabot please benchmark name=file-*": {
        "ursa-i9-9960x": (filter_with_file_only_benchmarks, None),
        "ursa-thinkcentre-m75q": (
            {"name": "file-*"},
            "Only ['lang', 'command'] filters are supported on ursa-thinkcentre-m75q",
        ),
        "new-machine": (
            {"name": "file-*"},
            "Only ['lang', 'command'] filters are supported on new-machine",
        ),
    },
    "@ursabot please benchmark command=cpp-micro --suite-filter=arrow-compute-vector-selection-benchmark --benchmark-filter=TakeStringRandomIndicesWithNulls/262144/2 --iterations=3 --show-output=true": {
        "ursa-i9-9960x": (
            {
                "command": "cpp-micro --suite-filter=arrow-compute-vector-selection-benchmark --benchmark-filter=TakeStringRandomIndicesWithNulls/262144/2 --iterations=3 --show-output=true",
            },
            "Only ['lang', 'name'] filters are supported on ursa-i9-9960x",
        ),
        "ursa-thinkcentre-m75q": (
            {
                "command": "cpp-micro --suite-filter=arrow-compute-vector-selection-benchmark --benchmark-filter=TakeStringRandomIndicesWithNulls/262144/2 --iterations=3 --show-output=true",
            },
            None,
        ),
        "new-machine": (
            {
                "command": "cpp-micro --suite-filter=arrow-compute-vector-selection-benchmark --benchmark-filter=TakeStringRandomIndicesWithNulls/262144/2 --iterations=3 --show-output=true",
            },
            None,
        ),
    },
}

pull_comments_with_unsupported_ursabot_commands = [
    "@ursabot",
    "@ursabot hello",
    "@ursabot help",
    "@ursabot please benchmark lang=Julia",
    "@ursabot please benchmark something=something",
    "@ursabot please benchmark lang=Python lang=C++",
    "@ursabot please benchmark name=file-write lang=C++",
]


def verify_benchmarkables_and_builds_were_created_for_pull_request_comment(
    response, expected_runs
):
    assert response.status_code == 202
    assert response.json == ""
    assert len(Benchmarkable.all()) == 2
    assert len(Run.all()) == 2 * len(list(machine_configs.keys()))

    benchmarkable = Benchmarkable.get(test_benchmarkable_id)
    baseline_benchmarkable = Benchmarkable.get(test_baseline_benchmarkable_id)

    assert benchmarkable
    assert baseline_benchmarkable
    assert benchmarkable.baseline_id == test_baseline_benchmarkable_id
    assert benchmarkable.pull_number == test_pull_number
    assert benchmarkable.pull_notification().message == {
        "url": "http://mocked-integrations:9999/github/repos/apache/arrow/issues/comments/1234",
        "body": "test",
    }
    for machine_name, (
        expected_filters,
        expected_skip_reason,
    ) in expected_runs.items():
        machine = Machine.get(machine_name)
        machine_run = benchmarkable.machine_run(machine)
        print(machine_run.machine_name)
        print(machine_run.skip_reason)
        print(machine_run.filters)
        assert machine_run.filters == expected_filters
        assert machine_run.skip_reason == expected_skip_reason
        if expected_skip_reason:
            assert machine_run.status == "skipped"
        else:
            assert machine_run.status == "scheduled"
        assert (
            baseline_benchmarkable.machine_run(machine).filters
            == machine.default_filters["arrow-commit"]
        )


def test_post_events_for_pr_with_supported_ursabot_commands(client):
    for (
        comment,
        expected_runs,
    ) in pull_comments_with_expected_machine_run_filters_and_skip_reason.items():
        print(comment)
        delete_data()
        update_machine_configs(machine_configs)
        mock_offline_machine()
        response = make_github_webhook_event_for_comment(client, comment)
        verify_benchmarkables_and_builds_were_created_for_pull_request_comment(
            response, expected_runs
        )


def test_post_events_for_pr_with_unsupported_ursabot_commands(client):
    for comment in pull_comments_with_unsupported_ursabot_commands:
        response = make_github_webhook_event_for_comment(client, comment)

        assert response.status_code == 202
        assert response.json == ""
        assert len(Benchmarkable.all()) == 0
        assert outbound_requests[-1] == (
            f"http://mocked-integrations:9999/github/repos/apache/arrow/issues/{test_pull_number}/comments",
            json.dumps({"body": (benchmark_command_examples)}),
        )


def test_post_events_for_pr_with_existing_results(client):
    # Create runs with ALL benchmarks for PR baseline and contender commits
    expected_runs = pull_comments_with_expected_machine_run_filters_and_skip_reason[
        "@ursabot please benchmark"
    ]
    response = make_github_webhook_event_for_comment(client)
    verify_benchmarkables_and_builds_were_created_for_pull_request_comment(
        response, expected_runs
    )

    # Verify PR requests with benchmark filters do not create new runs
    # for PR baseline and contender commits with existing runs with ALL benchmarks
    for comment in [
        "@ursabot please benchmark lang=Python",
        "@ursabot please benchmark lang=C++",
        "@ursabot please benchmark lang=R",
        "@ursabot please benchmark name=file-write",
        "@ursabot please benchmark command=cpp-micro --suite-filter=arrow-compute-vector-selection-benchmark",
    ]:
        response = make_github_webhook_event_for_comment(client, comment)
        assert response.status_code == 202
        assert response.json == ""
        assert len(Benchmarkable.all()) == 2
        assert len(Run.all()) == 2 * len(list(machine_configs.keys()))
        assert outbound_requests[-1] == (
            f"http://mocked-integrations:9999/github/repos/apache/arrow/issues/{test_pull_number}/comments",
            json.dumps({"body": "Commit sha2 already has scheduled benchmark runs."}),
        )


def test_github_request_signature(client, monkeypatch):
    Config.GITHUB_REPOS_WITH_BENCHMARKABLE_COMMITS["apache/arrow"][
        "github_secret"
    ] = "test"
    response = make_github_webhook_event_for_comment(client)
    Config.GITHUB_REPOS_WITH_BENCHMARKABLE_COMMITS["apache/arrow"][
        "github_secret"
    ] = "github_secret"
    assert response.status_code == 401
    assert (
        response.json
        == "Github's actual X-Hub-Signature-256 dit not match expected X-Hub-Signature-256."
    )
