from config import Config
from db import Session
from models.machine import Machine


def update_machine_configs(machine_configs=None):
    if not machine_configs:
        machine_configs = Config.MACHINES

    for machine_name, params in machine_configs.items():
        machine = Machine.get(machine_name)
        if machine:
            machine.update(params)
        else:
            try:
                params["name"] = machine_name
                machine = Machine(**params)
                machine.create_benchmark_pipeline()
                Session.add(machine)
                Session.commit()
            except Exception as e:
                Session.rollback()
                raise e

    for machine in Machine.all():
        if machine.name not in machine_configs:
            machine.delete_benchmark_pipeline()
            for run in machine.runs:
                run.delete()
            machine.delete()
