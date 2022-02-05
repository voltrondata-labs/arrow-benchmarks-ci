import re

from config import Config
from models.benchmarkable import Benchmarkable
from integrations.github import Github
from logger import log

# apache/arrow commits into master branch have messages
# that contain originating pull request number in phrases like "\n\nCloses #10973 from ..."
pattern = "\nCloses #(.*) from"
compiled_pattern = re.compile(pattern)


def get_originating_pull_number(commit_dict):
    try:
        return (
            compiled_pattern.search(commit_dict["commit"]["message"]).group(1).strip()
        )
    except Exception as e:
        log.error(
            f"Unable to get originating pull number for commit = {commit_dict['sha']} "
            f"from message = {commit_dict['commit']['message']}"
        )
        log.exception(e)


def get_commits_for_repo(repo, benchmarkable_type):
    commit_dicts = Github(repo).get_commits()
    commit_dicts.reverse()

    for commit_dict in commit_dicts:
        pull_number = get_originating_pull_number(commit_dict)

        Benchmarkable.create(
            dict(
                id=commit_dict["sha"],
                type=benchmarkable_type,
                data=commit_dict,
                baseline_id=commit_dict["parents"][-1]["sha"],
                reason=benchmarkable_type,
                pull_number=pull_number,
            )
        )


def get_commits():
    for repo, params in Config.GITHUB_REPOS_WITH_BENCHMARKABLE_COMMITS.items():
        get_commits_for_repo(repo, params["benchmarkable_type"])
