from models.notification import Notification


def publish_benchmark_alerts_on_pull_requests():
    notifications = (
        Notification.query()
        .filter(
            Notification.finished_at.is_(None),
            Notification.type == "pull_comment_alert",
        )
        .all()
    )

    for notification in notifications:
        if not notification.benchmarkable.baseline:
            continue

        if not notification.all_runs_with_publishable_benchmark_results_finished():
            continue

        comment_body = (
            notification.generate_pull_comment_body_for_high_regression_alert(
                benchmark_langs_filter=["Python", "R"]
            )
        )
        if comment_body:
            notification.create_pull_comment(comment_body)

        notification.mark_finished()
