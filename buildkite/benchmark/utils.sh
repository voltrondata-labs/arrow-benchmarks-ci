#!/bin/bash

init_conda() {
  if [ -d "/var/lib/buildkite-agent" ]; then
    eval "$(command '/var/lib/buildkite-agent/miniconda3/bin/conda' 'shell.bash' 'hook' 2> /dev/null)"
  else
    eval "$(command '/root/miniconda3/bin/conda' 'shell.bash' 'hook' 2> /dev/null)"
  fi
}

create_conda_env_for_arrow_commit() {
  git clone "${ARROW_REPO}"
  pushd arrow
  git fetch -v --prune -- origin "${BENCHMARKABLE}"
  git checkout -f "${BENCHMARKABLE}"
  source dev/conbench_envs/hooks.sh create_conda_env_with_arrow_python
  popd
}

create_conda_env_for_pyarrow_apache_wheel() {
  conda create -y -n pyarrow-apache-wheel -c conda-forge \
    python="${PYTHON_VERSION}" \
    pandas
  conda activate pyarrow-apache-wheel
  pip install "${BENCHMARKABLE}"
}

create_conda_env_with_arrow() {
  if [ "${BENCHMARKABLE_TYPE}" = "arrow-commit" ]
  then
    echo "Creating conda env for arrow commit"
    create_conda_env_for_arrow_commit
  else
    echo "Creating conda env for pyarrow apache wheel"
    create_conda_env_for_pyarrow_apache_wheel
  fi
}

install_conbench() {
  git clone https://github.com/conbench/conbench.git
  pushd conbench
  pip install -r requirements-cli.txt
  pip install -U PyYAML
  python setup.py install
  popd
}

build_arrow_r() {
  pushd arrow
  source dev/conbench_envs/hooks.sh build_arrow_r
  popd
}

build_arrow_java() {
  pushd arrow
  source dev/conbench_envs/hooks.sh build_arrow_java
  popd
}

install_archery() {
  rm -rf arrow
  git clone "${ARROW_REPO}"
  pushd arrow
  git fetch -v --prune -- origin "${BENCHMARKABLE}"
  git checkout -f "${BENCHMARKABLE}"
  source dev/conbench_envs/hooks.sh install_archery
  popd
}

install_arrowbench() {
  # do I need to cd into benchmarks dir?
  git clone https://github.com/ursacomputing/arrowbench.git
  R -e "remotes::install_local('./arrowbench')"
}

install_duckdb_r_with_tpch() {
  # Workaround for intermittent but frequent Duckdb R installation issues which should be fixed soon by DuckDB
  cp -R /tmp/duckdb/DBI /var/lib/buildkite-agent/miniconda3/envs/arrow-commit/lib/R/library/DBI
  cp -R /tmp/duckdb/duckdb /var/lib/buildkite-agent/miniconda3/envs/arrow-commit/lib/R/library/duckdb

  # Duckdb R was installed on voltron-pavilion and ursa-i9-9960x manually using this script:
  #
  #  sudo su
  #  su - buildkite-agent
  #
  #  eval "$(command '/var/lib/buildkite-agent/miniconda3/bin/conda' 'shell.bash' 'hook' 2> /dev/null)"
  #  conda activate arrow-commit
  #  export HOME=/var/lib/buildkite-agent/
  #  cd ~
  #
  #  git clone https://github.com/duckdb/duckdb.git
  #
  #  cd duckdb
  #  git fetch --tags
  #  latestTag=$(git describe --tags `git rev-list --tags --max-count=1`)
  #  git checkout $latestTag
  #
  #  cd tools/rpkg
  #  R -e "remotes::install_deps()"
  #  DUCKDB_R_EXTENSIONS=tpch R CMD INSTALL .
  #
  #  mkdir /tmp/duckdb
  #  cp -R /var/lib/buildkite-agent/miniconda3/envs/arrow-commit/lib/R/library/DBI /tmp/duckdb/DBI
  #  cp -R /var/lib/buildkite-agent/miniconda3/envs/arrow-commit/lib/R/library/duckdb /tmp/duckdb/duckdb
  #  ls -al /tmp/duckdb
}

install_java_script_project_dependencies() {
  pushd arrow
  source dev/conbench_envs/hooks.sh install_java_script_project_dependencies
  popd
}

create_data_dir() {
  mkdir -p "${BENCHMARKS_DATA_DIR}"
  mkdir -p "${BENCHMARKS_DATA_DIR}/temp"
}

build_arrow_and_run_benchmark_groups() {
  export ARROW_REPO=https://github.com/apache/arrow.git
  source buildkite/benchmark/utils.sh init_conda
  source buildkite/benchmark/utils.sh create_conda_env_with_arrow
  source buildkite/benchmark/utils.sh install_conbench
  python -m buildkite.benchmark.run_benchmark_groups
  conda deactivate
}

"$@"
