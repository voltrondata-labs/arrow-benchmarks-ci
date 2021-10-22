from integrations.pypi import pypi
from models.benchmarkable import Benchmarkable

benchmarkable_type = reason = "pyarrow-apache-wheel"


def get_pyarrow_versions():
    pyarrow_versions = pypi.get_pyarrow_versions_in_desc_order()
    benchmarkable_id = f"pyarrow=={pyarrow_versions[0]}"
    benchmarkable_baseline_id = f"pyarrow=={pyarrow_versions[1]}"

    Benchmarkable.create(
        dict(
            id=benchmarkable_id,
            type=benchmarkable_type,
            baseline_id=benchmarkable_baseline_id,
            reason=reason,
        )
    )

    Benchmarkable.create(
        dict(
            id=benchmarkable_baseline_id,
            type=benchmarkable_type,
            reason=reason,
        )
    )
