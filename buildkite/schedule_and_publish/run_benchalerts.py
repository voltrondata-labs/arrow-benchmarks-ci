import os

from integrations.slack import Slack
from logger import log
from models.benchalerts_run import BenchalertsRun


def run_one_benchalerts_run(benchalerts_run: BenchalertsRun) -> None:
    """Run an unfinished benchalerts run."""
    log.info(
        f"Run {benchalerts_run.id} for benchmarkable {benchalerts_run.benchmarkable_id}"
    )
    if not benchalerts_run.ready_to_run:
        log.info("Benchmarks are not finished yet")
        return

    benchalerts_run.run_benchalerts()
    log.info(
        f"Finished benchalerts run. Status: {benchalerts_run.status}, check link: "
        f"{benchalerts_run.check_link}, comment link: {benchalerts_run.pr_comment_link}"
    )

    # TODO: move this Slack step into the BenchalertsRun.run_benchalerts() pipeline
    if benchalerts_run.status == "action_required":
        msg = (
            f"The `benchalerts` run for {benchalerts_run.reason} "
            f"`{benchalerts_run.benchmarkable_id[:7]}` had benchmark failures. Please "
            f"see the report for more details: {benchalerts_run.pr_comment_link}"
        )
    elif benchalerts_run.status == "failure":
        msg = (
            f"The `benchalerts` run for {benchalerts_run.reason} "
            f"`{benchalerts_run.benchmarkable_id[:7]}` had benchmarks indicating a "
            "performance regression. Please see the report for more details: "
            f"{benchalerts_run.pr_comment_link}"
        )
    else:
        return

    log.info(f"Posting to Slack: {msg}")
    Slack().post_message(msg)


def run_benchalerts():
    unfinished_runs = BenchalertsRun.search([BenchalertsRun.finished_at.is_(None)])
    log.info(
        f"Looking at unfinished benchalerts runs: {[r.id for r in unfinished_runs]}"
    )
    benchalerts_errors = []

    for benchalerts_run in unfinished_runs:
        try:
            run_one_benchalerts_run(benchalerts_run)
        except Exception as e:
            log.exception(f"Error running benchalerts: {repr(e)}")
            benchalerts_errors.append(e)

    if benchalerts_errors:
        raise RuntimeError(f"Errors running benchalerts: {repr(benchalerts_errors)}")


if __name__ == "__main__":
    try:
        run_benchalerts()
    except Exception as e:
        Slack().post_message(
            repr(e) + "\n\nBuild log: " + os.getenv("BUILDKITE_BUILD_URL", "<missing>")
        )
        raise
