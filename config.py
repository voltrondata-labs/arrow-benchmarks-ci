import getpass
import os


class Config:
    BUILDKITE_API_BASE_URL = os.getenv("BUILDKITE_API_BASE_URL")
    BUILDKITE_API_TOKEN = os.getenv("BUILDKITE_API_TOKEN")
    BUILDKITE_ORG = os.getenv("BUILDKITE_ORG")

    CONBENCH_URL = os.getenv("CONBENCH_URL")

    DB_HOST = os.environ.get("DB_HOST", "localhost")
    DB_NAME = os.environ.get("DB_NAME", "postgres")
    DB_PASSWORD = os.environ.get("DB_PASSWORD", "postgres")
    DB_PORT = os.environ.get("DB_PORT", "5432")
    DB_USERNAME = os.environ.get("DB_USERNAME", getpass.getuser())

    ENV = os.environ.get("ENV")

    GITHUB_API_BASE_URL = os.getenv("GITHUB_API_BASE_URL")
    GITHUB_API_TOKEN = os.getenv("GITHUB_API_TOKEN")
    GITHUB_REPOS_WITH_BENCHMARKABLE_COMMITS = {
        "apache/arrow": {
            "benchmarkable_type": "arrow-commit",
            "enable_benchmarking_for_pull_requests": True,
            "github_secret": os.getenv("GITHUB_SECRET"),
            "publish_benchmark_results_on_pull_requests": True,
        },
        "ElenaHenderson/benchmarkable-repo": {
            "benchmarkable_type": "benchmarkable-repo-commit",
            "enable_benchmarking_for_pull_requests": False,
            "github_secret": None,
            "publish_benchmark_results_on_pull_requests": False,
        },
        "apache/arrow-rs": {
            "benchmarkable_type": "arrow-rs-commit",
            "enable_benchmarking_for_pull_requests": False,
            "github_secret": None,
            "publish_benchmark_results_on_pull_requests": False,
        },
        "apache/arrow-datafusion": {
            "benchmarkable_type": "arrow-datafusion-commit",
            "enable_benchmarking_for_pull_requests": False,
            "github_secret": None,
            "publish_benchmark_results_on_pull_requests": False,
        },
    }
    GITHUB_REPO = os.getenv("GITHUB_REPO")
    MAX_COMMITS_TO_FETCH = os.getenv("MAX_COMMITS_TO_FETCH", 20)

    PIPY_API_BASE_URL = os.getenv("PIPY_API_BASE_URL")
    PIPY_PROJECT = os.getenv("PIPY_PROJECT")

    PYTHON_VERSION_FOR_BENCHMARK_BUILDS = "3.8"

    SECRET = os.getenv("SECRET")

    SLACK_API_BASE_URL = os.getenv("SLACK_API_BASE_URL")
    SLACK_API_TOKEN = os.getenv("SLACK_API_TOKEN")
    SLACK_CHANNEL_FOR_BENCHMARK_RESULTS = os.getenv(
        "SLACK_CHANNEL_FOR_BENCHMARK_RESULTS"
    )
    SLACK_USER_ID_FOR_WARNINGS = os.getenv("SLACK_USER_ID_FOR_WARNINGS")

    SQLALCHEMY_DATABASE_URI = (
        f"postgresql://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    )

    MACHINES = {
        "ursa-i9-9960x": {
            "info": "Supported benchmark langs: Python, R, JavaScript. Skips certain "
            "commit messages if they contain certain strings.",
            "default_filters": {
                "arrow-commit": {
                    "langs": {
                        "Python": {
                            "names": [
                                "csv-read",
                                "dataframe-to-table",
                                "dataset-filter",
                                "dataset-read",
                                "dataset-select",
                                "dataset-selectivity",
                                "dataset-serialize",
                                "file-read",
                                "file-write",
                                "recursive-get-file-info",
                                "wide-dataframe",
                            ]
                        },
                        "R": {
                            "names": [
                                "dataframe-to-table",
                                "file-read",
                                "file-write",
                                "partitioned-dataset-filter",
                                "wide-dataframe",
                                "tpch",
                            ]
                        },
                        "JavaScript": {"names": ["js-micro"]},
                    },
                    "commit_message_skip_strings": [
                        "[C#]",
                        "[CI]",
                        "[Doc]",
                        "[Docs]",
                        "[Go]",
                        "[Java]",
                        "[MATLAB]",
                    ],
                },
                "pyarrow-apache-wheel": {
                    "langs": {
                        "Python": {
                            "names": [
                                "csv-read",
                                "dataframe-to-table",
                                "dataset-filter",
                                "dataset-read",
                                "dataset-select",
                                "dataset-selectivity",
                                "dataset-serialize",
                                "file-read",
                                "file-write",
                                "recursive-get-file-info",
                                "wide-dataframe",
                            ]
                        }
                    },
                },
            },
            "supported_filters": ["lang", "name"],
            "offline_warning_enabled": True,
            "publish_benchmark_results": True,
            "max_builds": 1,
        },
        "ursa-thinkcentre-m75q": {
            "info": "Supported benchmark langs: C++, Java",
            "default_filters": {
                "arrow-commit": {
                    "langs": {
                        "C++": {"names": ["cpp-micro"]},
                        "Java": {"names": ["java-micro"]},
                    }
                }
            },
            "supported_filters": ["lang", "command"],
            "offline_warning_enabled": True,
            "publish_benchmark_results": True,
            "max_builds": 1,
        },
        "ec2-t3-xlarge-us-east-2": {
            "info": "Supported benchmark langs: Python, R. Runs only benchmarks with cloud = True",
            "default_filters": {
                "arrow-commit": {
                    "langs": {
                        "Python": {
                            "names": [
                                "dataset-read",
                                "dataset-select",
                            ]
                        },
                    }
                },
                "benchmarkable-repo-commit": {
                    "langs": {
                        "Python": {
                            "names": [
                                "simple-benchmark",
                            ]
                        }
                    }
                },
            },
            "supported_filters": ["lang", "name"],
            "offline_warning_enabled": False,
            "publish_benchmark_results": True,
            "max_builds": 1,
        },
        "test-mac-arm": {
            "info": "Supported benchmark langs: C++, Python, R",
            "default_filters": {
                "arrow-commit": {
                    "langs": {
                        "C++": {"names": ["cpp-micro"]},
                        "R": {"names": ["tpch"]},
                    }
                },
            },
            "supported_filters": ["lang", "name"],
            "offline_warning_enabled": False,
            "publish_benchmark_results": True,
            "max_builds": 1,
        },
        "arm64-t4g-linux-compute": {
            "info": "Supported benchmark langs: C++, Python, R",
            "default_filters": {
                "arrow-commit": {
                    "langs": {
                        "Python": {"names": ["dataset-read", "dataset-select"]},
                        "C++": {"names": ["cpp-micro"]},
                        "R": {"names": ["tpch"]},
                    }
                },
            },
            "supported_filters": ["lang", "name"],
            "offline_warning_enabled": False,
            "publish_benchmark_results": False,
            "max_builds": 2,
        },
        "arm64-m6g-linux-compute": {
            "info": "Supported benchmark langs: C++, Python, R",
            "default_filters": {
                "arrow-commit": {
                    "langs": {
                        "Python": {"names": ["dataset-read", "dataset-select"]},
                        "C++": {"names": ["cpp-micro"]},
                        "R": {"names": ["tpch"]},
                    }
                },
            },
            "supported_filters": ["lang", "name"],
            "offline_warning_enabled": False,
            "publish_benchmark_results": False,
            "max_builds": 2,
        },
        "ec2-m5-4xlarge-us-east-2": {
            "info": "Supported benchmark langs: R",
            "default_filters": {
                "arrow-commit": {
                    "langs": {
                        "R": {"names": ["tpch"]},
                    }
                },
            },
            "supported_filters": ["lang", "name"],
            "offline_warning_enabled": False,
            "publish_benchmark_results": False,
            "max_builds": 2,
        },
    }
