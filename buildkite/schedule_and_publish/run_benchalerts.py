import os

from integrations.slack import Slack
from logger import log
from models.benchalerts_run import BenchalertsRun


def run_benchalerts():
    unfinished_runs = BenchalertsRun.search([BenchalertsRun.finished_at.is_(None)])
    log.info(
        f"Looking at unfinished benchalerts runs: {[r.id for r in unfinished_runs]}"
    )
    errors = []

    for run in unfinished_runs:
        log.info(f"Run {run.id} for benchmarkable {run.benchmarkable_id}")
        if not run.ready_to_run:
            log.info("Benchmarks are not finished yet")
            continue

        try:
            run.run_benchalerts()
        except Exception as e:
            log.exception(f"Error running benchalerts: {repr(e)}")
            errors.append(e)

    if errors:
        raise RuntimeError(f"Errors running benchalerts: {repr(errors)}")


if __name__ == "__main__":
    try:
        run_benchalerts()
    except Exception as e:
        Slack().post_message(
            repr(e) + "\n\nBuild log: " + os.getenv("BUILDKITE_BUILD_URL")
        )
