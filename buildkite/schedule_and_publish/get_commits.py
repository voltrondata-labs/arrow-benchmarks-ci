from config import Config
from models.benchmarkable import Benchmarkable
from integrations.github import Github
from logger import log


def get_originating_pull_number(github, commit_dict):
    try:
        return github.get_pulls(commit_dict["sha"])[0]["number"]
    except Exception as e:
        log.error(
            f"Unable to get originating pull number for commit = {commit_dict['sha']} "
            f"from message = {commit_dict['commit']['message']}"
        )
        log.exception(e)


def get_commits_for_repo(repo, benchmarkable_type):
    github = Github(repo)
    commit_dicts = github.get_commits()
    commit_dicts.reverse()

    for commit_dict in commit_dicts:
        pull_number = get_originating_pull_number(github, commit_dict)

        if len(commit_dict["parents"]) > 0:
            baseline_id = commit_dict["parents"][-1]["sha"]
        else:
            baseline_id = None

        Benchmarkable.create(
            dict(
                id=commit_dict["sha"],
                type=benchmarkable_type,
                data=commit_dict,
                baseline_id=baseline_id,
                reason=benchmarkable_type,
                pull_number=pull_number,
            )
        )


def get_commits():
    for repo, params in Config.GITHUB_REPOS_WITH_BENCHMARKABLE_COMMITS.items():
        get_commits_for_repo(repo, params["benchmarkable_type"])
