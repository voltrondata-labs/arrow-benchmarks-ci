import os
import subprocess
import sys


def context():
    import pyarrow

    build_info = pyarrow.cpp_build_info
    return {
        "arrow_compiler_id": build_info.compiler_id,
        "arrow_compiler_version": build_info.compiler_version,
        "arrow_compiler_flags": build_info.compiler_flags,
    }


def machine_info():
    sys.path.append("conbench")
    from conbench.machine_info import machine_info

    return machine_info(os.getenv("MACHINE"))


def conda_packages():
    result = subprocess.run(["conda", "list", "-e"], stdout=subprocess.PIPE)
    return result.stdout.decode()


def run_context():
    return {
        "context": context(),
        "machine_info": machine_info(),
        "conda_packages": conda_packages(),
    }
