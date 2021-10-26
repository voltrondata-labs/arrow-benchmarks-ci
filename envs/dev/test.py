import subprocess
import time
from datetime import datetime, timedelta

from buildkite.deploy.update_machine_configs import update_machine_configs
from buildkite.schedule_and_publish.get_commits import get_commits
from buildkite.schedule_and_publish.get_pyarrow_versions import get_pyarrow_versions
from buildkite.schedule_and_publish.create_benchmark_builds import (
    create_benchmark_builds,
)
from buildkite.schedule_and_publish.update_benchmark_builds_status import (
    update_benchmark_builds_status,
)
from buildkite.schedule_and_publish.publish_warnings_on_slack import (
    publish_buildkite_build_warnings_on_slack,
    publish_offline_machine_warnings_on_slack,
)
from buildkite.schedule_and_publish.publish_benchmark_results_on_slack import (
    publish_benchmark_results_on_slack,
)

from models.benchmarkable import Benchmarkable
from models.run import Run
from tests.helpers import mock_offline_machine


def mock_long_running_build():
    run = Run.first(status="created")
    run.buildkite_data = {
        "started_at": (datetime.utcnow() - timedelta(hours=3)).strftime(
            "%Y-%m-%dT%H:%M:%S.%fZ"
        ),
        "web_url": "mocked.buildkite.url.com",
    }
    run.status = "scheduled"
    run.save()


def cleanup_mock_long_running_build():
    run = Run.first(status="scheduled")
    run.buildkite_data = None
    run.status = "created"
    run.save()


print("\n-------Recreating db\n")
subprocess.run(
    "source envs/dev-conda/private_env;"
    "dropdb postgres;"
    "createdb postgres;"
    "alembic upgrade head",
    capture_output=True,
    shell=True,
    executable="/bin/bash",
)

print("\n-------Testing get_commits() and get_pyarrow_versions()\n")
update_machine_configs()
get_commits()
get_pyarrow_versions()

print("\n-------Testing publish_buildkite_build_warnings_on_slack()\n")
mock_long_running_build()
publish_buildkite_build_warnings_on_slack()
cleanup_mock_long_running_build()

print("\n-------Testing publish_offline_machine_warnings_on_slack()\n")
mock_offline_machine()
publish_offline_machine_warnings_on_slack()

print(
    "\n-------Testing create_benchmark_builds() and update_benchmark_builds_status()\n"
)
create_benchmark_builds()
time.sleep(15)
update_benchmark_builds_status()
for run in Run.all():
    print(run.benchmarkable_id, run.reason, run.status, run.skip_reason)


print("\n-------Testing publish_benchmark_results_on_slack()\n")
create_benchmark_builds()
time.sleep(15)
update_benchmark_builds_status()
for benchmarkable in Benchmarkable.all():
    print(
        benchmarkable.id,
        benchmarkable.all_runs_finished(),
        benchmarkable.baseline.all_runs_finished() if benchmarkable.baseline else "",
    )
publish_benchmark_results_on_slack()
