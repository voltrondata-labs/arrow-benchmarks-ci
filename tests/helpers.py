from copy import deepcopy

from config import Config
from models.benchmark_group_execution import BenchmarkGroupExecution
from models.benchmarkable import Benchmarkable
from models.machine import Machine
from models.memory_usage import MemoryUsage
from models.notification import Notification
from models.run import Run


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
