from datetime import timedelta

from config import Config
from models.machine import Machine
from models.run import Run
from integrations.slack import slack

max_benchmark_build_run_time_hours = 2.45


def publish_offline_machine_warnings_on_slack():
    warnings = []

    for machine in Machine.all():
        if (
            machine.offline_warning_enabled
            and (machine.hostname or machine.ip_address)
            and not machine.is_reachable()
        ):
            warning = f":warning: {machine.name} is offline."
            warnings.append(warning)
            slack.post_message(f"{warning} cc: <@{Config.SLACK_USER_ID_FOR_WARNINGS}>")

    return warnings


def publish_buildkite_build_warnings_on_slack():
    warnings = []

    for run in Run.all(status="scheduled"):
        if (
            run.buildkite_build_run_time_until_now
            and run.buildkite_build_run_time_until_now
            > timedelta(hours=max_benchmark_build_run_time_hours)
        ):
            warning = f":warning: Benchmark build {run.buildkite_build_web_url} is running > {max_benchmark_build_run_time_hours} hours."
            warnings.append(warning)
            slack.post_message(f"{warning} cc: <@{Config.SLACK_USER_ID_FOR_WARNINGS}>")

    return warnings
