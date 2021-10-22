from models.run import Run


def update_benchmark_builds_status():
    for run in Run.all(status="scheduled"):
        run.update_buildkite_data()
        run.mark_finished()
