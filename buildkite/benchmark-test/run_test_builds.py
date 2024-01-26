import json
import os

from config import Config
from integrations.buildkite import buildkite
from utils import generate_uuid


def run_test_builds():
    machines = os.getenv("MACHINES").split("\n")
    branch = os.getenv("BRANCH")
    commit = os.getenv("COMMIT")
    message = run_name = f"Test Build for branch={branch} and commit={commit}"
    benchmarkable_type = "arrow-commit"

    for machine in machines:
        env = {
            "BENCHMARKABLE": "HEAD",
            "BENCHMARKABLE_TYPE": benchmarkable_type,
            "FILTERS": json.dumps(
                Config.MACHINES[machine]["default_filters"][benchmarkable_type]
            ),
            "MACHINE": machine,
            "RUN_ID": generate_uuid(),
            "RUN_NAME": run_name,
            "RUN_REASON": "test",
            "PYTHON_VERSION": Config.PYTHON_VERSION_FOR_BENCHMARK_BUILDS,
        }
        build = buildkite.create_build(
            pipeline_name=f"Arrow BCI Benchmark on {machine}",
            commit=commit,
            branch=branch,
            message=message,
            env=env,
        )
        print(f"Created {run_name}: {build['web_url']}")


run_test_builds()
