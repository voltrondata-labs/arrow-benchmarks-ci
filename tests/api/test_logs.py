import json
from copy import deepcopy
from datetime import datetime, timedelta

from buildkite.schedule_and_publish.get_commits import get_commits
from models.benchmark_group_execution import BenchmarkGroupExecution
from models.machine import Machine
from models.memory_usage import MemoryUsage
from models.run import Run
from utils import generate_uuid

benchmark_group_execution_id = generate_uuid()
memory_usage_id = generate_uuid()

benchmark_group_execution_data = {
    "type": "BenchmarkGroupExecution",
    "id": benchmark_group_execution_id,
    "lang": "Python",
    "name": "file-read",
    "options": "options",
    "flags": "flags",
    "benchmarkable_id": "1",
    "run_id": "run_id",
    "run_name": "rune_name",
    "machine": "machine",
    "process_pid": 2,
    "command": "command",
    "started_at": str(datetime.now() - timedelta(minutes=3)),
    "finished_at": str(datetime.now()),
    "total_run_time": str(timedelta(minutes=3)),
    "failed": True,
    "return_code": 137,
    "stderr": "stderr",
    "total_machine_virtual_memory": 16624467968,
}
memory_usage_data = {
    "type": "MemoryUsage",
    "id": memory_usage_id,
    "benchmark_group_execution_id": benchmark_group_execution_id,
    "process_pid": 3,
    "parent_process_pid": 2,
    "process_name": "R",
    "process_cmdline": [
        "/var/lib/buildkite-agent/miniconda3/envs/arrow-commit/lib/R/bin/exec/R",
        "-e",
        'library(arrowbench);~+~run_one(write_file,~+~source="nyctaxi_2010-01",~+~format="feather",~+~compression="lz4",~+~input="data_frame",~+~cpu_count=NULL)',
    ],
    "mem_percent": 0.4413227066347222,
    "mem_rss_bytes": 27533,
}


def log_benchmark_group_execution(client, data=None, api_access_token=None):
    get_commits()
    machine = Machine.first()

    if not data:
        run = Run.first(machine_name=machine.name)
        data = deepcopy(benchmark_group_execution_data)
        data["run_id"] = run.id

    if not api_access_token:
        api_access_token = machine.generate_api_access_token()

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_access_token}",
    }

    return client.post("/logs", data=json.dumps(data), headers=headers)


def log_memory_usage(client, data=None, api_access_token=None):
    if not data:
        data = deepcopy(memory_usage_data)

    if not api_access_token:
        machine = Machine.first()
        api_access_token = machine.generate_api_access_token()

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_access_token}",
    }

    return client.post("/logs", data=json.dumps(data), headers=headers)


def test_benchmark_group_execution_logs_201(client):
    assert not BenchmarkGroupExecution.get(benchmark_group_execution_data["id"])
    response = log_benchmark_group_execution(client, data=None, api_access_token=None)
    assert response.status_code == 201
    assert BenchmarkGroupExecution.get(benchmark_group_execution_data["id"])


def test_benchmark_group_execution_logs_401_invalid_token(client):
    assert not BenchmarkGroupExecution.get(benchmark_group_execution_data["id"])
    response = log_benchmark_group_execution(
        client, data=None, api_access_token="invalid token"
    )
    assert response.status_code == 401
    assert not BenchmarkGroupExecution.get(benchmark_group_execution_data["id"])


def test_benchmark_group_execution_logs_401_invalid_run_id(client):
    assert not BenchmarkGroupExecution.get(benchmark_group_execution_data["id"])
    response = log_benchmark_group_execution(
        client, data=benchmark_group_execution_data, api_access_token=None
    )
    assert response.status_code == 401
    assert not BenchmarkGroupExecution.get(benchmark_group_execution_data["id"])


def test_memory_usage_logs_201(client):
    assert not MemoryUsage.get(memory_usage_data["id"])
    machine = Machine.first()
    api_access_token = machine.generate_api_access_token()
    log_benchmark_group_execution(client, data=None, api_access_token=api_access_token)
    response = log_memory_usage(client, data=None, api_access_token=api_access_token)
    assert response.status_code == 201
    assert MemoryUsage.get(memory_usage_data["id"])


def test_memory_usage_logs_401_invalid_token(client):
    assert not MemoryUsage.get(memory_usage_data["id"])
    machine = Machine.first()
    api_access_token = machine.generate_api_access_token()
    log_benchmark_group_execution(client, data=None, api_access_token=api_access_token)
    response = log_memory_usage(client, data=None, api_access_token="invalid token")
    assert response.status_code == 401
    assert not MemoryUsage.get(memory_usage_data["id"])


def test_memory_usage_logs_401_not_existing_benchmark_execution_group(client):
    assert not MemoryUsage.get(memory_usage_data["id"])
    machine = Machine.first()
    api_access_token = machine.generate_api_access_token()
    log_benchmark_group_execution(client, data=None, api_access_token=api_access_token)
    data = deepcopy(memory_usage_data)
    data["benchmark_group_execution_id"] = "not_existing_benchmark_execution_group_id"
    response = log_memory_usage(client, data=data, api_access_token=api_access_token)
    assert response.status_code == 401
    assert not MemoryUsage.get(memory_usage_data["id"])


def test_memory_usage_logs_401_unauthorized_machine(client):
    assert not MemoryUsage.get(memory_usage_data["id"])
    machines = Machine.all()
    api_access_token_1 = machines[0].generate_api_access_token()
    api_access_token_2 = machines[1].generate_api_access_token()
    log_benchmark_group_execution(
        client, data=None, api_access_token=api_access_token_1
    )
    response = log_memory_usage(client, data=None, api_access_token=api_access_token_2)
    assert response.status_code == 401
    assert not MemoryUsage.get(memory_usage_data["id"])
