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
        print('>>>>>>>')
        print(notification.benchmarkable.id)
        if not notification.benchmarkable.baseline:
            continue

        if not notification.all_runs_with_publishable_benchmark_results_finished():
            print("Here!")
            continue

        if notification.benchmarkable.has_high_level_of_regressions():
            notification.create_pull_comment(
                "Benchmarks have high level of regressions"
            )

        notification.mark_finished()
