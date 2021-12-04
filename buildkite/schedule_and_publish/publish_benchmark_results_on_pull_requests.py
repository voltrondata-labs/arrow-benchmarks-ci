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

        new_comment_body = notification.generate_pull_comment_body()

        if not notification.pull_comment_body:
            notification.create_pull_comment(new_comment_body)

        if notification.pull_comment_body != new_comment_body:
            notification.update_pull_comment(new_comment_body)

        if notification.all_runs_with_publishable_benchmark_results_finished():
            notification.mark_finished()
