import os

from .run import Run, repos_with_benchmark_groups


def run_benchmark_groups():
    for repo in repos_with_benchmark_groups:
        if repo["benchmarkable_type"] == os.getenv("BENCHMARKABLE_TYPE"):
            run = Run(repo)
            run.run_all_benchmark_groups()


run_benchmark_groups()
