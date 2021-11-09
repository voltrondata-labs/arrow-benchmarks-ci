from models.notification import Notification


def publish_benchmark_results_on_pull_requests():
    notifications = (
        Notification.query()
        .filter(Notification.finished_at.is_(None), Notification.type == "pull_comment")
        .all()
    )

    for notification in notifications:
        new_comment_body = notification.generate_pull_comment_body()

        # TODO: remove this code once done testing
        if notification.pull_number not in [1234, 9272]:
            print(notification.pull_number)
            print(new_comment_body)
            continue

        if not notification.pull_comment_body:
            notification.create_pull_comment(new_comment_body)

        if notification.pull_comment_body != new_comment_body:
            notification.update_pull_comment(new_comment_body)

        if notification.all_runs_finished():
            notification.mark_finished()
