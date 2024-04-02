from copy import deepcopy
from pathlib import Path

from buildkite.benchmark.run import MockRun, repos_with_benchmark_groups
from tests.helpers import (
    machine_configs,
    filter_with_r_only_benchmarks,
    filter_with_python_only_benchmarks,
    filter_with_cpp_only_benchmarks,
    filter_with_file_only_benchmarks,
)

expected_setup_commands = [
    ("git clone https://github.com/voltrondata-labs/benchmarks.git", ".", True),
    ("git fetch && git checkout main", "benchmarks", True),
    ("pip install -e .", "benchmarks", True),
]

expected_setup_commands_for_cpp_benchmarks = []

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
        'conbench csv-read ALL --iterations=3 --drop-caches=true --run-id=$RUN_ID --run-name="$RUN_NAME" --run-reason="$RUN_REASON"',
        "benchmarks",
        False,
    ),
    (
        'conbench dataframe-to-table ALL --iterations=3 --drop-caches=true --run-id=$RUN_ID --run-name="$RUN_NAME" --run-reason="$RUN_REASON"',
        "benchmarks",
        False,
    ),
    (
        'conbench dataset-filter ALL --iterations=3 --drop-caches=true --run-id=$RUN_ID --run-name="$RUN_NAME" --run-reason="$RUN_REASON"',
        "benchmarks",
        False,
    ),
    (
        'conbench dataset-read ALL --iterations=1 --all=true --drop-caches=true --run-id=$RUN_ID --run-name="$RUN_NAME" --run-reason="$RUN_REASON"',
        "benchmarks",
        False,
    ),
    (
        'conbench dataset-select ALL --iterations=3 --drop-caches=true --run-id=$RUN_ID --run-name="$RUN_NAME" --run-reason="$RUN_REASON"',
        "benchmarks",
        False,
    ),
    (
        'conbench dataset-selectivity ALL --iterations=3 --all=true --drop-caches=true --run-id=$RUN_ID --run-name="$RUN_NAME" --run-reason="$RUN_REASON"',
        "benchmarks",
        False,
    ),
    (
        'conbench file-read ALL --iterations=3 --all=true --drop-caches=true --run-id=$RUN_ID --run-name="$RUN_NAME" --run-reason="$RUN_REASON"',
        "benchmarks",
        False,
    ),
    (
        'conbench file-write ALL --iterations=3 --all=true --drop-caches=true --run-id=$RUN_ID --run-name="$RUN_NAME" --run-reason="$RUN_REASON"',
        "benchmarks",
        False,
    ),
    (
        'conbench wide-dataframe --iterations=3 --all=true --drop-caches=true --run-id=$RUN_ID --run-name="$RUN_NAME" --run-reason="$RUN_REASON"',
        "benchmarks",
        False,
    ),
]

expected_commands_for_r_benchmarks = expected_setup_commands_for_r_benchmarks + [
    (
        'conbench dataframe-to-table ALL --iterations=3 --drop-caches=true --language=R --run-id=$RUN_ID --run-name="$RUN_NAME" --run-reason="$RUN_REASON"',
        "benchmarks",
        False,
    ),
    (
        'conbench file-read ALL --iterations=3 --all=true --drop-caches=true --language=R --run-id=$RUN_ID --run-name="$RUN_NAME" --run-reason="$RUN_REASON"',
        "benchmarks",
        False,
    ),
    (
        'conbench file-write ALL --iterations=3 --all=true --drop-caches=true --language=R --run-id=$RUN_ID --run-name="$RUN_NAME" --run-reason="$RUN_REASON"',
        "benchmarks",
        False,
    ),
    (
        'conbench partitioned-dataset-filter --iterations=3 --all=true --drop-caches=true --run-id=$RUN_ID --run-name="$RUN_NAME" --run-reason="$RUN_REASON"',
        "benchmarks",
        False,
    ),
]

expected_commands_for_cpp_benchmarks = expected_setup_commands_for_cpp_benchmarks + [
    (
        'conbench cpp-micro --iterations=1 --run-id=$RUN_ID --run-name="$RUN_NAME" --run-reason="$RUN_REASON"',
        "benchmarks",
        False,
    ),
]

expected_commands_for_cpp_benchmarks_with_one_command_only = expected_setup_commands_for_cpp_benchmarks + [
    (
        'conbench cpp-micro --suite-filter=arrow-compute-vector-selection-benchmark --benchmark-filter=TakeStringRandomIndicesWithNulls/262144/2 --iterations=3  --run-id=$RUN_ID --run-name="$RUN_NAME" --run-reason="$RUN_REASON"',
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
                'conbench dataset-read ALL --iterations=1 --all=true --drop-caches=true --run-id=$RUN_ID --run-name="$RUN_NAME" --run-reason="$RUN_REASON"',
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
                'conbench file-read ALL --iterations=3 --all=true --drop-caches=true --run-id=$RUN_ID --run-name="$RUN_NAME" --run-reason="$RUN_REASON"',
                "benchmarks",
                False,
            ),
            (
                'conbench file-write ALL --iterations=3 --all=true --drop-caches=true --run-id=$RUN_ID --run-name="$RUN_NAME" --run-reason="$RUN_REASON"',
                "benchmarks",
                False,
            ),
        ]
        + expected_setup_commands_for_r_benchmarks
        + [
            (
                'conbench file-read ALL --iterations=3 --all=true --drop-caches=true --language=R --run-id=$RUN_ID --run-name="$RUN_NAME" --run-reason="$RUN_REASON"',
                "benchmarks",
                False,
            ),
            (
                'conbench file-write ALL --iterations=3 --all=true --drop-caches=true --language=R --run-id=$RUN_ID --run-name="$RUN_NAME" --run-reason="$RUN_REASON"',
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
    repo = [
        deepcopy(x)
        for x in repos_with_benchmark_groups
        if x["repo"].endswith("voltrondata-labs/benchmarks.git")
    ][0]
    # These tests should use benchmarks.json in benchmarks repo but should not be affected any new benchmarks
    # that added since 2b217db086260ab3bb243e26253b7c1de0180777
    repo["url_for_benchmark_groups_list_json"] = (
        "https://raw.githubusercontent.com/voltrondata-labs/benchmarks/2b217db086260ab3bb243e26253b7c1de0180777/benchmarks.json"
    )
    for test in tests:
        print(test)
        run = MockRun(repo, test["run_filters"])
        run.benchmarkable_type = "arrow-commit"
        run.run_all_benchmark_groups()
        assert run.executor.executed_commands == test["expected_commands"]


def test_run_arrowbench_benchmarks(monkeypatch):
    run_id = "fake-run-id"
    run_name = "test-run-name"
    run_reason = "test"
    monkeypatch.setenv("RUN_ID", run_id)
    monkeypatch.setenv("RUN_NAME", run_name)
    monkeypatch.setenv("RUN_REASON", run_reason)

    repo = [
        deepcopy(x)
        for x in repos_with_benchmark_groups
        if x["repo"].endswith("arrowbench.git")
    ][0]
    # These tests should use benchmarks.json in arrowbench repo but should not be affected any new benchmarks
    # that added since c5e5af241f17d27aadc01548f283a2a977151b91
    repo["url_for_benchmark_groups_list_json"] = (
        "https://raw.githubusercontent.com/voltrondata-labs/arrowbench/c5e5af241f17d27aadc01548f283a2a977151b91/inst/benchmarks.json"
    )

    filter_with_arrowbench_r_only_benchmarks = deepcopy(filter_with_r_only_benchmarks)
    filter_with_arrowbench_r_only_benchmarks["langs"]["R"]["names"] = [
        "arrowbench/" + name
        for name in filter_with_arrowbench_r_only_benchmarks["langs"]["R"]["names"]
    ]

    expected_setup_commands = (
        [
            ("git clone https://github.com/voltrondata-labs/arrowbench.git", ".", True),
            ("git fetch && git checkout main", "arrowbench", True),
        ]
        + expected_setup_commands_for_r_benchmarks
        + [
            (
                "pip install 'benchconnect@git+https://github.com/conbench/conbench.git@main#subdirectory=benchconnect' && R --vanilla -e 'stopifnot(arrowbench:::benchconnect_available())'",
                "arrowbench",
                True,
            ),
        ]
    )

    run = MockRun(repo, filters=filter_with_arrowbench_r_only_benchmarks)
    run.benchmarkable_type = "arrow-commit"
    run.run_all_benchmark_groups()
    assert run.executor.executed_commands[:-1] == expected_setup_commands
    run_command = run.executor.executed_commands[-1]
    # runs an ephemeral tempfile
    assert run_command[0].startswith("R --vanilla -f ")
    assert run_command[0].endswith(".R")
    assert run_command[1] == "arrowbench"
    assert run_command[2] is False
    tempfile_path = Path(run_command[0].split()[-1]).resolve()
    with open(tempfile_path, "r") as f:
        tempfile_lines = [line.strip() for line in f.readlines()]

    assert tempfile_lines == [
        "",
        "bm_df <- arrowbench::get_package_benchmarks()",
        "bm_names <- c('file-write', 'dataframe-to-table', "
        "'partitioned-dataset-filter', 'file-read')",
        "bm_df_filtered <- bm_df[bm_df$name %in% bm_names, ]",
        "",
        "# Benchmark names to run:",
        "print(bm_names)",
        "# Benchmark dataframe to run:",
        "print(bm_df_filtered)",
        "",
        "arrowbench::run(",
        "bm_df_filtered,",
        "n_iter = 3L,",
        "drop_caches = TRUE,",
        "publish = TRUE,",
        f"run_name = '{run_name}',",
        f"run_reason = '{run_reason}'",
        ")",
        "",
    ]

    tempfile_path.unlink()


def test_run_adapter_benchmarks():
    repo = [
        deepcopy(x)
        for x in repos_with_benchmark_groups
        if x["repo"].endswith("arrow-benchmarks-ci.git")
    ][0]
    # These tests should use benchmarks.json in arrow-benchmarks-ci repo but should not be affected any new benchmarks
    # that added since 1ca33e8800a11624faf89a85af817ca83e473f56
    repo["url_for_benchmark_groups_list_json"] = (
        "https://raw.githubusercontent.com/voltrondata-labs/arrow-benchmarks-ci/1ca33e8800a11624faf89a85af817ca83e473f56/adapters/benchmarks.json"
    )

    filters = {
        "langs": {
            "Python": {
                "names": [
                    "adapters/mock-adapter",
                ]
            }
        }
    }

    expected_setup_commands = [
        (
            "git clone https://github.com/voltrondata-labs/arrow-benchmarks-ci.git",
            ".",
            True,
        ),
        (
            "git fetch && git checkout main",
            "arrow-benchmarks-ci/adapters",
            True,
        ),
        ("pip install -r requirements.txt", "arrow-benchmarks-ci/adapters", True),
        ("source buildkite/benchmark/utils.sh create_data_dir", ".", True),
    ]

    expected_run_commands = [
        ("python mock-adapter.py", "arrow-benchmarks-ci/adapters", False)
    ]

    run = MockRun(repo, filters=filters)
    run.benchmarkable_type = "arrow-commit"
    run.run_all_benchmark_groups()
    assert (
        run.executor.executed_commands
        == expected_setup_commands + expected_run_commands
    )
