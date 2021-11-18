#!/bin/bash

eval "$(command '/root/miniconda3/bin/conda' 'shell.bash' 'hook' 2> /dev/null)"
export ARROW_REPO="https://github.com/apache/arrow.git" \
    BENCHMARKABLE_TYPE="arrow-commit" \
    BENCHMARKABLE="641554b0bcce587549bfcfd0cde3cb4bc23054aa" \
    PYTHON_VERSION="3.8" \
    BENCHMARKS_DATA_DIR="/test" \
    FILTERS="{}" \
    RUN_ID="testable-builds" \
    RUN_NAME="testable-builds" \
    MACHINE="docker-test" \
    CONBENCH_URL="https://conbench.ursa.dev"

source buildkite/benchmark/utils.sh create_conda_env_with_arrow
source buildkite/benchmark/utils.sh install_conbench
python -m buildkite.benchmark.run_benchmark_groups
