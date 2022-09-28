import os

from integrations.buildkite import buildkite


def run_test_builds():
    machines = os.getenv("MACHINES_WITH_TEST_BUILDS")
    print(machines)
    print(buildkite.get_scheduled_builds("arrow-bci-benchmark-on-ursa-i9-9960x"))


run_test_builds()
