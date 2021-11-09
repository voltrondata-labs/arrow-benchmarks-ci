import hashlib
import hmac
import json
from copy import deepcopy

from config import Config
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


def machine_configs():
    configs = {}
    for machine in ["ursa-i9-9960x", "ursa-thinkcentre-m75q"]:
        configs[machine] = deepcopy(Config.MACHINES[machine])
    return configs


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
