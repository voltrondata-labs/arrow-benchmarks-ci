import json
import os

from config import Config
from integrations.buildkite import buildkite
from utils import generate_uuid


def run_test_builds():
    machines = os.getenv("MACHINES").split("\n")
    branch = os.getenv("BRANCH")
    commit = os.getenv("COMMIT")
    message = os.getenv("MESSAGE")
    benchmarkable_type = "arrow-commit"
    print(machines, branch, commit, message)

    for machine in machines:
        env = {
            "BENCHMARKABLE": "HEAD",
            "BENCHMARKABLE_TYPE": benchmarkable_type,
            "FILTERS": json.dumps(
                Config.MACHINES[machine]["default_filters"][benchmarkable_type]
            ),
            "MACHINE": machine,
            "RUN_ID": generate_uuid(),
            "RUN_NAME": f"Test Build for branch={branch} and commit={commit}",
            "RUN_REASON": "test",
            "PYTHON_VERSION": Config.PYTHON_VERSION_FOR_BENCHMARK_BUILDS,
        }
        print(env)

    print(
        buildkite.get_scheduled_builds("arrow-bci-benchmark-on-ursa-i9-9960x")[0].keys()
    )


run_test_builds()
