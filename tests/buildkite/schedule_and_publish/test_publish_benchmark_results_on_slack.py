from buildkite.schedule_and_publish.create_benchmark_builds import \
    create_benchmark_builds
from buildkite.schedule_and_publish.get_commits import get_commits
from buildkite.schedule_and_publish.publish_benchmark_results_on_slack import \
    publish_benchmark_results_on_slack
from buildkite.schedule_and_publish.update_benchmark_builds_status import \
    update_benchmark_builds_status
from models.benchmarkable import Benchmarkable
from models.machine import Machine
from models.run import Run


def expected_slack_message(warning=""):
    benchmarkable = Benchmarkable.get("41529c76fe80d1fe8e60b52c0da3669c901a45bb")
    compare_link1 = benchmarkable.conbench_compare_runs_web_url(
        Machine.get("ursa-i9-9960x")
    )
    compare_link2 = benchmarkable.conbench_compare_runs_web_url(
        Machine.get("ursa-thinkcentre-m75q")
    )

    return (
        "Benchmark results for commit: 41529c76fe80d1fe8e60b52c0da3669c901a45bb\n"
        "contender <https://github.com/apache/arrow/commit/41529c76fe80d1fe8e60b52c0da3669c901a45bb|`41529c76`> ARROW-8453: [Go][Integration] Support  [author: <https://github.com/test|test>]\n"
        "baseline <https://github.com/apache/arrow/commit/8a540a1edb755e2c465202315058494ed3e72b39|`8a540a1e`> ARROW-8780: [Python][Doc] Document  [author: <https://github.com/test|test>]:\n"
        "Conbench compare runs links:\n"
        f"[Finished :arrow_down:33.33% :arrow_up:33.33%{warning}] <{compare_link1}|ursa-i9-9960x>\n"
        f"[Failed :arrow_down:33.33% :arrow_up:33.33%] <{compare_link2}|ursa-thinkcentre-m75q>\n"
        "Buildkite builds:\n"
        "[Finished] <https://buildkite.com/apache-arrow/arrow-bci-benchmark-on-ursa-i9-9960x/builds/1| `41529c76` ursa-i9-9960x>\n"
        "[Failed] <https://buildkite.com/apache-arrow/arrow-bci-benchmark-on-ursa-thinkcentre-m75q/builds/1| `41529c76` ursa-thinkcentre-m75q>\n"
        "[Finished] <https://buildkite.com/apache-arrow/arrow-bci-benchmark-on-ursa-i9-9960x/builds/1| `8a540a1e` ursa-i9-9960x>\n"
        "[Failed] <https://buildkite.com/apache-arrow/arrow-bci-benchmark-on-ursa-thinkcentre-m75q/builds/1| `8a540a1e` ursa-thinkcentre-m75q>\n"
    )


def test_publish_benchmark_results_on_slack():
    get_commits()

    # Iteration 1
    create_benchmark_builds()
    assert len(Run.all(status="scheduled")) == 2
    assert len(Run.all(status="finished")) == 0
    assert len(Run.all(status="failed")) == 0

    update_benchmark_builds_status()
    assert len(Run.all(status="scheduled")) == 0
    assert len(Run.all(status="finished")) == 1
    assert len(Run.all(status="failed")) == 1

    messages = publish_benchmark_results_on_slack()
    assert messages == []

    # Iteration 2
    create_benchmark_builds()
    assert len(Run.all(status="scheduled")) == 2
    assert len(Run.all(status="finished")) == 1
    assert len(Run.all(status="failed")) == 1

    update_benchmark_builds_status()
    assert len(Run.all(status="scheduled")) == 0
    assert len(Run.all(status="finished")) == 2
    assert len(Run.all(status="failed")) == 2

    messages = publish_benchmark_results_on_slack()
    assert messages == [expected_slack_message()]


def test_publish_benchmark_results_on_slack_with_context_changed_warning():
    get_commits()

    # Iteration 1
    create_benchmark_builds()
    update_benchmark_builds_status()
    publish_benchmark_results_on_slack()

    # Iteration 2
    create_benchmark_builds()
    update_benchmark_builds_status()

    run = Run.first(status="finished")
    run.context = {"1": "1"}
    run.save()

    messages = publish_benchmark_results_on_slack()
    assert messages == [
        expected_slack_message(
            " :warning: Contender and baseline run contexts do not match"
        )
    ]
