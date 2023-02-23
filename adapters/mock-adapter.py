import json
from typing import Any, Dict, List

from benchadapt import BenchmarkResult
from benchadapt.adapters import BenchmarkAdapter

RESULTS_DICT = {
    "run_name": "very-real-benchmark",
    "run_id": "ezf69672dc3741259aac97650414a18c",
    "batch_id": "1z21bd2477d04ca8be0f4bad58c61757",
    "run_reason": None,
    "timestamp": "2202-09-16T15:42:27.527948+00:00",
    "stats": {
        "data": [1.1, 2.2, 3.3],
        "unit": "ns",
        "times": [3.3, 2.2, 1.1],
        "time_unit": "ns",
    },
    "tags": {
        "name": "very-real-benchmark",
        "suite": "dope-benchmarks",
        "source": "app-micro",
    },
    "info": {},
    "context": {"benchmark_language": "A++"},
    "github": {
        "commit": "2z8c9c49a5dc4a179243268e4bb6daa5",
        "repository": "git@github.com:conchair/conchair",
    },
}


class MockAdapter(BenchmarkAdapter):
    def __init__(
        self,
        result_fields_override: Dict[str, Any] = None,
        result_fields_append: Dict[str, Any] = None,
    ) -> None:
        super().__init__(
            command=["echo", "hello"],
            result_fields_override=result_fields_override,
            result_fields_append=result_fields_append,
        )

    def _transform_results(self) -> List[BenchmarkResult]:
        return [BenchmarkResult(**RESULTS_DICT)]


if __name__ == "__main__":
    adapter = MockAdapter()
    adapter.transform_results()

    results_dicts = [res.to_publishable_dict() for res in adapter.results]
    print(json.dumps(results_dicts, indent=2))
