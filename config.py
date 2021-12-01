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
    GITHUB_REPO_WITH_BENCHMARKABLE_COMMITS = os.getenv(
        "GITHUB_REPO_WITH_BENCHMARKABLE_COMMITS"
    )
    GITHUB_REPO = os.getenv("GITHUB_REPO")
    GITHUB_SECRET = os.getenv("GITHUB_SECRET")
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
        "machine1": {
            "info": "name = dataset-filter",
            "default_filters": {
                "arrow-commit": {"name": "dataset-filter"},
            },
            "supported_filters": ["name"],
            "supported_langs": ["Python"],
            "offline_warning_enabled": False,
        },
        "machine2": {
            "info": "name = dataset-filter",
            "default_filters": {
                "arrow-commit": {"name": "dataset-filter"},
            },
            "supported_filters": ["name"],
            "supported_langs": ["Python"],
            "offline_warning_enabled": False,
        },
        # "ursa-i9-9960x": {
        #     "info": "langs = Python, R, JavaScript",
        #     "default_filters": {
        #         "arrow-commit": {"lang": "Python,R,JavaScript"},
        #         "pyarrow-apache-wheel": {"lang": "Python"},
        #     },
        #     "supported_filters": ["lang", "name"],
        #     "supported_langs": ["Python", "R", "JavaScript"],
        #     "offline_warning_enabled": True,
        # },
        # "ursa-thinkcentre-m75q": {
        #     "info": "langs = C++, Java",
        #     "default_filters": {
        #         "arrow-commit": {"lang": "C++,Java"},
        #     },
        #     "supported_filters": ["lang", "command"],
        #     "supported_langs": ["C++", "Java"],
        #     "offline_warning_enabled": True,
        # },
        # "ec2-t3-xlarge-us-east-2": {
        #     "info": "cloud = True",
        #     "default_filters": {
        #         "arrow-commit": {"flags": {"cloud": True}},
        #         "pyarrow-apache-wheel": {"lang": "Python", "flags": {"cloud": True}},
        #     },
        #     "supported_filters": ["lang", "name"],
        #     "supported_langs": ["Python", "R", "C++"],
        #     "offline_warning_enabled": False,
        # },
    }
