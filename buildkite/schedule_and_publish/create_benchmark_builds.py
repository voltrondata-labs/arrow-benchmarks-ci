from models.machine import Machine
from models.run import Run


def create_benchmark_builds_for_pulls(machine):
    unscheduled_runs = Run.all(
        limit=None,
        order_by="created_at",
        **dict(
            machine_name=machine,
            status="created",
            reason="pull-request",
        ),
    )
    for unscheduled_run in unscheduled_runs:
        unscheduled_baseline_run = Run.first(
            **dict(
                benchmarkable_id=unscheduled_run.benchmarkable.baseline_id,
                machine_name=machine,
                status="created",
            )
        )
        if unscheduled_baseline_run:
            unscheduled_baseline_run.create_benchmark_build()

        unscheduled_run.create_benchmark_build()


def create_benchmark_builds():
    for machine in Machine.all():
        create_benchmark_builds_for_pulls(machine.name)

        if machine.has_scheduled_or_running_builds():
            continue

        unscheduled_runs = Run.all(
            limit=1,
            order_by="created_at",
            **dict(machine_name=machine.name, status="created"),
        )
        if len(unscheduled_runs) > 0:
            unscheduled_runs[0].create_benchmark_build()
