import json
import requests

from config import Config
from integrations import adapter

PATH_TO_BENCHMARK_PIPELINE_YML = "buildkite/benchmark/pipeline.yml"


class Buildkite:
    def __init__(self):
        self.session = requests.Session()
        self.session.mount("https://", adapter)
        self.session.headers = {"Authorization": f"Bearer {Config.BUILDKITE_API_TOKEN}"}
        self.base_url = (
            f"{Config.BUILDKITE_API_BASE_URL}/v2/organizations/{Config.BUILDKITE_ORG}"
        )

    def create_pipeline(self, pipeline_name, agent_queue):
        # TODO: Remove line below once done with testing
        agent_queue = "arrow-benchmarks-ci-test"

        url = f"{self.base_url}/pipelines"
        data = {
            "name": pipeline_name,
            "repository": f"https://github.com/{Config.GITHUB_REPO}.git",
            "default_branch": "main",
            # TODO: Update to main once done with testing
            "branch_configuration": "",
            "provider": {
                "id": "github",
                "settings": {
                    "trigger_mode": "none",
                    "build_pull_requests": False,
                    "pull_request_branch_filter_enabled": False,
                    "skip_builds_for_existing_commits": False,
                    "skip_pull_request_builds_for_existing_commits": True,
                    "build_pull_request_ready_for_review": False,
                    "build_pull_request_labels_changed": False,
                    "build_pull_request_forks": False,
                    "prefix_pull_request_fork_branch_names": True,
                    "build_branches": True,
                    "build_tags": False,
                    "cancel_deleted_branch_builds": False,
                    "publish_commit_status": True,
                    "publish_commit_status_per_step": False,
                    "separate_pull_request_statuses": False,
                    "publish_blocked_as_pending": False,
                    "use_step_key_as_commit_status": False,
                    "filter_enabled": True,
                    "repository": Config.GITHUB_REPO,
                },
            },
            "configuration": f'agents:\n  queue: "{agent_queue}"\nsteps:\n  - label: ":pipeline: Pipeline upload"\n    command: buildkite-agent pipeline upload {PATH_TO_BENCHMARK_PIPELINE_YML}\n',
            "steps": [
                {
                    "type": "script",
                    "name": ":pipeline: Pipeline upload",
                    "command": f"buildkite-agent pipeline upload {PATH_TO_BENCHMARK_PIPELINE_YML}",
                    "artifact_paths": None,
                    "branch_configuration": None,
                    "env": {},
                    "timeout_in_minutes": None,
                    "agent_query_rules": [],
                    "concurrency": None,
                    "parallelism": None,
                }
            ],
        }
        return self.session.post(url, data=json.dumps(data)).json()

    def delete_pipeline(self, name):
        url = f"{self.base_url}/pipelines/{name.replace(' ', '-').lower()}"
        return self.session.delete(url)

    def create_build(self, pipeline_name, commit, branch, message, env):
        # TODO: remove this
        branch = "add-dev-env-and-buildkite-pipelines"
        url = f"{self.base_url}/pipelines/{pipeline_name.replace(' ', '-').lower()}/builds"
        data = {
            "commit": commit,
            "branch": branch,
            "message": message,
            "env": env,
        }
        return self.session.post(url, data=json.dumps(data)).json()

    def get_build(self, buildkite_build_url):
        return self.session.get(buildkite_build_url).json()

    def get_scheduled_builds(self, pipeline_name):
        url = f"{self.base_url}/pipelines/{pipeline_name.replace(' ', '-').lower()}/builds?branch=main&state[]=scheduled&state[]=running"
        return self.session.get(url).json()


buildkite = Buildkite()
