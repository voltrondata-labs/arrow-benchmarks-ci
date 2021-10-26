from models.notification import Notification


def publish_benchmark_results_on_slack():
    notifications = (
        Notification.query()
        .filter(
            Notification.finished_at.is_(None), Notification.type == "slack_message"
        )
        .all()
    )

    messages = []

    for notification in notifications:
        if notification.all_runs_finished():
            text = notification.generate_slack_message_text()
            notification.post_slack_message(text)
            notification.mark_finished()
            messages.append(text)

    return messages
