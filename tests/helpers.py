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
        "info": "Supported benchmark langs: Python, R, JavaScript",
        "default_filters": {
            "arrow-commit": {
                "langs": {
                    "Python": {
                        "names": [
                            "csv-read",
                            "dataframe-to-table",
                            "dataset-filter",
                            "dataset-read",
                            "dataset-select",
                            "dataset-selectivity",
                            "file-read",
                            "file-write",
                            "wide-dataframe",
                        ]
                    },
                    "R": {
                        "names": [
                            "dataframe-to-table",
                            "file-read",
                            "file-write",
                            "partitioned-dataset-filter",
                            "wide-dataframe",
                        ]
                    },
                    "JavaScript": {"names": ["js-micro"]},
                }
            },
            "pyarrow-apache-wheel": {
                "langs": {
                    "Python": {
                        "names": [
                            "csv-read",
                            "dataframe-to-table",
                            "dataset-filter",
                            "dataset-read",
                            "dataset-select",
                            "dataset-selectivity",
                            "file-read",
                            "file-write",
                            "wide-dataframe",
                        ]
                    }
                },
            },
        },
        "supported_filters": ["lang", "name"],
        "offline_warning_enabled": True,
        "publish_benchmark_results": True,
    },
    "ursa-thinkcentre-m75q": {
        "info": "Supported benchmark langs: C++, Java",
        "default_filters": {
            "arrow-commit": {
                "langs": {
                    "C++": {"names": ["cpp-micro"]},
                    "Java": {"names": ["java-micro"]},
                }
            }
        },
        "supported_filters": ["lang", "command"],
        "offline_warning_enabled": True,
        "publish_benchmark_results": True,
    },
    "new-machine": {
        "info": "Supported benchmark langs: C++, Java",
        "default_filters": {
            "arrow-commit": {
                "langs": {
                    "C++": {"names": ["cpp-micro"]},
                    "Java": {"names": ["java-micro"]},
                }
            }
        },
        "supported_filters": ["lang", "command"],
        "offline_warning_enabled": False,
        "publish_benchmark_results": False,
    },
}

filter_with_python_only_benchmarks = {
    "langs": {
        "Python": {
            "names": [
                "csv-read",
                "dataframe-to-table",
                "dataset-filter",
                "dataset-read",
                "dataset-select",
                "dataset-selectivity",
                "file-read",
                "file-write",
                "wide-dataframe",
            ]
        }
    }
}

filter_with_r_only_benchmarks = {
    "langs": {
        "R": {
            "names": [
                "dataframe-to-table",
                "file-read",
                "file-write",
                "partitioned-dataset-filter",
                "wide-dataframe",
            ]
        }
    }
}


filter_with_cpp_only_benchmarks = {
    "langs": {
        "C++": {"names": ["cpp-micro"]},
    }
}

filter_with_java_script_only_benchmarks = {
    "langs": {
        "JavaScript": {"names": ["js-micro"]},
    }
}

filter_with_file_write_only_benchmarks = {
    "langs": {
        "Python": {"names": ["file-write"]},
        "R": {
            "names": [
                "file-write",
            ]
        },
        "JavaScript": {"names": []},
    }
}

filter_with_file_write_python_only_benchmarks = {
    "langs": {
        "Python": {
            "names": [
                "file-write",
            ]
        }
    }
}

filter_with_file_only_benchmarks = {
    "langs": {
        "Python": {"names": ["file-read", "file-write"]},
        "R": {"names": ["file-read", "file-write"]},
        "JavaScript": {"names": []},
    }
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
