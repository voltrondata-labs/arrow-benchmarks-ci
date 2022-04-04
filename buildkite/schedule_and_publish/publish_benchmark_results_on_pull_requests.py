from models.notification import Notification


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

        new_comment_body = notification.generate_pull_comment_body()

        if not notification.pull_comment_body:
            notification.create_pull_comment(new_comment_body)

        if notification.pull_comment_body != new_comment_body:
            notification.update_pull_comment(new_comment_body)

        if notification.all_runs_with_publishable_benchmark_results_finished():
            notification.mark_finished()
