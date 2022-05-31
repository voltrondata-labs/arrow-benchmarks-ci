from copy import deepcopy

from buildkite.benchmark.run import MockRun, repos_with_benchmark_groups
from tests.helpers import (
    machine_configs,
    filter_with_r_only_benchmarks,
    filter_with_python_only_benchmarks,
    filter_with_cpp_only_benchmarks,
    filter_with_file_only_benchmarks,
)

expected_setup_commands = [
    ("git clone https://github.com/ursacomputing/benchmarks.git", ".", True),
    ("git fetch && git checkout main", "benchmarks", True),
    ("python setup.py develop", "benchmarks", True),
]

expected_setup_commands_for_cpp_benchmarks = [
    ("source buildkite/benchmark/utils.sh install_archery", ".", True),
]

expected_setup_commands_for_r_benchmarks = [
    ("source buildkite/benchmark/utils.sh build_arrow_r", ".", True),
    ("source buildkite/benchmark/utils.sh install_arrowbench", ".", True),
    ("source buildkite/benchmark/utils.sh create_data_dir", ".", True),
]

expected_setup_commands_for_python_benchmarks = [
    ("source buildkite/benchmark/utils.sh create_data_dir", ".", True)
]


expected_commands_for_python_benchmarks = expected_setup_commands_for_python_benchmarks + [
    (
        'conbench csv-read ALL --iterations=3 --drop-caches=true --run-id=$RUN_ID --run-name="$RUN_NAME"',
        "benchmarks",
        False,
    ),
    (
        'conbench dataframe-to-table ALL --iterations=3 --drop-caches=true --run-id=$RUN_ID --run-name="$RUN_NAME"',
        "benchmarks",
        False,
    ),
    (
        'conbench dataset-filter ALL --iterations=3 --drop-caches=true --run-id=$RUN_ID --run-name="$RUN_NAME"',
        "benchmarks",
        False,
    ),
    (
        'conbench dataset-read ALL --iterations=1 --all=true --drop-caches=true --run-id=$RUN_ID --run-name="$RUN_NAME"',
        "benchmarks",
        False,
    ),
    (
        'conbench dataset-select ALL --iterations=3 --drop-caches=true --run-id=$RUN_ID --run-name="$RUN_NAME"',
        "benchmarks",
        False,
    ),
    (
        'conbench dataset-selectivity ALL --iterations=3 --all=true --drop-caches=true --run-id=$RUN_ID --run-name="$RUN_NAME"',
        "benchmarks",
        False,
    ),
    (
        'conbench file-read ALL --iterations=3 --all=true --drop-caches=true --run-id=$RUN_ID --run-name="$RUN_NAME"',
        "benchmarks",
        False,
    ),
    (
        'conbench file-write ALL --iterations=3 --all=true --drop-caches=true --run-id=$RUN_ID --run-name="$RUN_NAME"',
        "benchmarks",
        False,
    ),
    (
        'conbench wide-dataframe --iterations=3 --all=true --drop-caches=true --run-id=$RUN_ID --run-name="$RUN_NAME"',
        "benchmarks",
        False,
    ),
]

expected_commands_for_r_benchmarks = expected_setup_commands_for_r_benchmarks + [
    (
        'conbench dataframe-to-table ALL --iterations=3 --drop-caches=true --language=R --run-id=$RUN_ID --run-name="$RUN_NAME"',
        "benchmarks",
        False,
    ),
    (
        'conbench file-read ALL --iterations=3 --all=true --drop-caches=true --language=R --run-id=$RUN_ID --run-name="$RUN_NAME"',
        "benchmarks",
        False,
    ),
    (
        'conbench file-write ALL --iterations=3 --all=true --drop-caches=true --language=R --run-id=$RUN_ID --run-name="$RUN_NAME"',
        "benchmarks",
        False,
    ),
    (
        'conbench partitioned-dataset-filter --iterations=3 --all=true --drop-caches=true --run-id=$RUN_ID --run-name="$RUN_NAME"',
        "benchmarks",
        False,
    ),
]

expected_commands_for_cpp_benchmarks = expected_setup_commands_for_cpp_benchmarks + [
    (
        'conbench cpp-micro --iterations=1 --run-id=$RUN_ID --run-name="$RUN_NAME"',
        "benchmarks",
        False,
    ),
]

expected_commands_for_cpp_benchmarks_with_one_command_only = expected_setup_commands_for_cpp_benchmarks + [
    (
        'conbench cpp-micro --suite-filter=arrow-compute-vector-selection-benchmark --benchmark-filter=TakeStringRandomIndicesWithNulls/262144/2 --iterations=3  --run-id=$RUN_ID --run-name="$RUN_NAME"',
        "benchmarks",
        False,
    ),
]


tests = [
    {
        "run_filters": {},
        "expected_commands": expected_setup_commands
        + expected_commands_for_cpp_benchmarks
        + expected_commands_for_python_benchmarks
        + expected_commands_for_r_benchmarks,
    },
    {
        "run_filters": filter_with_python_only_benchmarks,
        "expected_commands": expected_setup_commands
        + expected_commands_for_python_benchmarks,
    },
    {
        "run_filters": filter_with_r_only_benchmarks,
        "expected_commands": expected_setup_commands
        + expected_commands_for_r_benchmarks,
    },
    {
        "run_filters": filter_with_cpp_only_benchmarks,
        "expected_commands": expected_setup_commands
        + expected_commands_for_cpp_benchmarks,
    },
    {
        "run_filters": {"langs": {"Python": {"names": ["dataset-read"]}}},
        "expected_commands": expected_setup_commands
        + expected_setup_commands_for_python_benchmarks
        + [
            (
                'conbench dataset-read ALL --iterations=1 --all=true --drop-caches=true --run-id=$RUN_ID --run-name="$RUN_NAME"',
                "benchmarks",
                False,
            ),
        ],
    },
    {
        "run_filters": filter_with_file_only_benchmarks,
        "expected_commands": expected_setup_commands
        + expected_setup_commands_for_python_benchmarks
        + [
            (
                'conbench file-read ALL --iterations=3 --all=true --drop-caches=true --run-id=$RUN_ID --run-name="$RUN_NAME"',
                "benchmarks",
                False,
            ),
            (
                'conbench file-write ALL --iterations=3 --all=true --drop-caches=true --run-id=$RUN_ID --run-name="$RUN_NAME"',
                "benchmarks",
                False,
            ),
        ]
        + expected_setup_commands_for_r_benchmarks
        + [
            (
                'conbench file-read ALL --iterations=3 --all=true --drop-caches=true --language=R --run-id=$RUN_ID --run-name="$RUN_NAME"',
                "benchmarks",
                False,
            ),
            (
                'conbench file-write ALL --iterations=3 --all=true --drop-caches=true --language=R --run-id=$RUN_ID --run-name="$RUN_NAME"',
                "benchmarks",
                False,
            ),
        ],
    },
    {
        "run_filters": {
            "command": "cpp-micro --suite-filter=arrow-compute-vector-selection-benchmark --benchmark-filter=TakeStringRandomIndicesWithNulls/262144/2 --iterations=3"
        },
        "expected_commands": expected_setup_commands
        + expected_commands_for_cpp_benchmarks_with_one_command_only,
    },
    {
        "run_filters": machine_configs["ursa-i9-9960x"]["default_filters"][
            "arrow-commit"
        ],
        "expected_commands": expected_setup_commands
        + expected_commands_for_python_benchmarks
        + expected_commands_for_r_benchmarks,
    },
]


def test_run_benchmarks():
    repo = deepcopy(repos_with_benchmark_groups[0])
    # These tests should use benchmarks.json in benchmarks repo but should not be affected any new benchmarks
    # that added since 2b217db086260ab3bb243e26253b7c1de0180777
    repo[
        "url_for_benchmark_groups_list_json"
    ] = "https://raw.githubusercontent.com/ursacomputing/benchmarks/2b217db086260ab3bb243e26253b7c1de0180777/benchmarks.json"
    for test in tests:
        print(test)
        run = MockRun(repo, test["run_filters"])
        run.benchmarkable_type = "arrow-commit"
        run.run_all_benchmark_groups()
        assert run.executed_commands == test["expected_commands"]
