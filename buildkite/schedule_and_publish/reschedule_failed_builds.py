import os
from datetime import datetime, timedelta

from buildkite.schedule_and_publish.create_benchmark_builds import (
    create_benchmark_builds,
)
from models.run import Run


def reschedule_failed_builds():
    machines = os.getenv("MACHINES_WITH_FAILED_BUILDS")
    hours = int(os.getenv("HOURS_WITH_FAILED_BUILDS"))
    runs = Run.all(status="failed")

    print(
        f"Rescheduling failed builds created in the last {hours} hours for these machines: {machines}"
    )

    runs = [
        r
        for r in runs
        if r.created_at > datetime.now() - timedelta(hours=hours)
        and r.machine_name in machines
    ]

    print(f"Found {len(runs)} failed builds")

    # Set status to "created" for all failed builds
    for run in runs:
        run.status = "created"
        run.buildkite_data = None
        run.scheduled_at = None
        run.finished_at = None
        run.total_run_time = None
        run.context = None
        run.machine_info = None
        run.conda_packages = None
        run.save()
        print(
            f"Rescheduled failed build for {run.benchmarkable_id} on {run.machine_name}"
        )

    # Ensure each build has at least one benchalerts workflow still scheduled
    for run in runs:
        unfinished_benchalerts_runs = [
            benchalerts_run
            for benchalerts_run in run.benchmarkable.benchalerts_runs
            if benchalerts_run.finished_at is None
        ]
        if not unfinished_benchalerts_runs:
            run.benchmarkable.add_benchalerts_run(reason=run.reason)

    create_benchmark_builds()
