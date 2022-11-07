from models.notification import Notification
from benchalerts import update_github_check_based_on_regressions

def publish_benchmark_results_on_pull_requests():
    notifications = (
        Notification.query()
        .filter(Notification.finished_at.is_(None), Notification.type == "pull_comment")
        .all()
    )

    for notification in notifications:
        if not notification.benchmarkable.baseline:
            continue

        if (
            not notification.should_be_updated_for_each_finished_run()
            and not notification.all_runs_with_publishable_benchmark_results_finished()
        ):
            continue

        contender_sha = notification.benchmarkable.id
        org = "apache"
        repo = "arrow"
        # TODO: find a build URL to use?
        # os.environ["BUILD_URL"] = ""
        is_pull_request = notification.benchmarkable.reason == "pull-request"

        res = update_github_check_based_on_regressions(
            contender_sha=contender_sha,
            z_score_threshold=10,
            warn_if_baseline_isnt_parent=not is_pull_request,
            repo=f"{org}/{repo}",
        )
        print(res)

        if notification.all_runs_with_publishable_benchmark_results_finished():
            notification.mark_finished()
