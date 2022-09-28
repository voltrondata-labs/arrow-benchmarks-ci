import os


def run_test_builds():
    machines = os.getenv("MACHINES_WITH_TEST_BUILDS")
    print(machines)


run_test_builds()
