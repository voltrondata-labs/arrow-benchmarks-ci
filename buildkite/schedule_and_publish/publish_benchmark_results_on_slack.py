from logger import log
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
        try:
            if notification.all_runs_with_publishable_benchmark_results_finished():
                text = notification.generate_slack_message_text()
                notification.post_slack_message(text)
                notification.mark_finished()
                messages.append(text)
        except Exception as e:
            log.error(
                "Caught the following exception when trying to publish a slack message "
                "for notification ID '%s'. Continuing on.",
                notification.id,
            )
            log.exception(e)

    return messages
