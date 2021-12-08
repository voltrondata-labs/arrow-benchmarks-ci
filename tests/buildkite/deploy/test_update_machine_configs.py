from copy import deepcopy

from buildkite.deploy.update_machine_configs import update_machine_configs
from models.machine import Machine
from tests.helpers import machine_configs


def test_update_machine_configs_add_machines():
    # update_machine_configs is run before each unit test
    for machine_name, machine_params in machine_configs.items():
        machine = Machine.get(machine_name)
        assert machine

        for attribute in [
            "info",
            "default_filters",
            "supported_filters",
            "offline_warning_enabled",
        ]:
            assert getattr(machine, attribute) == machine_params[attribute]


def test_update_machine_configs_remove_machine():
    configs = deepcopy(machine_configs)
    machine_to_remove = list(configs.keys())[0]
    assert Machine.get(machine_to_remove)

    configs.pop(machine_to_remove)
    update_machine_configs(configs)
    assert not Machine.get(machine_to_remove)
