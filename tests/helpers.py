import hashlib
import hmac
import json

from models.benchmark_group_execution import BenchmarkGroupExecution
from models.benchmarkable import Benchmarkable
from models.machine import Machine
from models.memory_usage import MemoryUsage
from models.notification import Notification
from models.run import Run

outbound_requests = []
test_pull_number = 1234
test_benchmarkable_id = "sha2"
test_baseline_benchmarkable_id = "sha1"
machine_configs = {
    "ursa-i9-9960x": {
        "info": "langs = Python, R, JavaScript",
        "default_filters": {
            "arrow-commit": {"lang": "Python,R,JavaScript"},
            "pyarrow-apache-wheel": {"lang": "Python"},
        },
        "supported_filters": ["lang", "name"],
        "supported_langs": ["Python", "R", "JavaScript"],
        "offline_warning_enabled": True,
        "publish_benchmark_results": True,
    },
    "ursa-thinkcentre-m75q": {
        "info": "langs = C++, Java",
        "default_filters": {
            "arrow-commit": {"lang": "C++,Java"},
        },
        "supported_filters": ["lang", "command"],
        "supported_langs": ["C++", "Java"],
        "offline_warning_enabled": True,
        "publish_benchmark_results": True,
    },
    "new-machine": {
        "info": "langs = C++, Java",
        "default_filters": {
            "arrow-commit": {"lang": "C++,Java"},
        },
        "supported_filters": ["lang", "command"],
        "supported_langs": ["C++", "Java"],
        "offline_warning_enabled": False,
        "publish_benchmark_results": False,
    },
}


def delete_data():
    for model in [
        Run,
        Notification,
        Benchmarkable,
        Machine,
        BenchmarkGroupExecution,
        MemoryUsage,
    ]:
        model.delete_all()
        assert model.all() == []


def mock_offline_machine():
    machine = Machine.first(name="ursa-i9-9960x")
    machine.ip_address = "192.184.132.52"
    machine.hostname = "test"
    machine.port = 27
    machine.save()


def make_github_webhook_event_for_comment(
    client, comment_body="@ursabot please benchmark"
):
    # Send Github event with X-Hub-Signature-256
    event = {
        "action": "created",
        "issue": {"number": 1234},
        "comment": {"body": comment_body},
        "repository": {},
        "organization": {},
        "sender": {},
    }

    data = json.dumps(event).encode()

    signature = b"sha256=" + (
        hmac.new(
            key="github_secret".encode(),
            msg=data,
            digestmod=hashlib.sha256,
        )
        .hexdigest()
        .encode()
    )

    return client.post(
        "/events",
        data=data,
        headers={"X-Hub-Signature-256": signature},
    )
