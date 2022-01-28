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

  export ARROW_BUILD_TESTS=OFF
  export ARROW_BUILD_TYPE=release
  export ARROW_DEPENDENCY_SOURCE=AUTO
  export ARROW_DATASET=ON
  export ARROW_DEFAULT_MEMORY_POOL=mimalloc
  export ARROW_ENABLE_UNSAFE_MEMORY_ACCESS=true
  export ARROW_ENABLE_NULL_CHECK_FOR_GET=false
  export ARROW_FLIGHT=OFF
  export ARROW_GANDIVA=OFF
  export ARROW_HDFS=ON
  export ARROW_INSTALL_NAME_RPATH=OFF
  export ARROW_MIMALLOC=ON
  export ARROW_NO_DEPRECATED_API=ON
  export ARROW_ORC=ON
  export ARROW_PARQUET=ON
  export ARROW_PLASMA=ON
  export ARROW_PYTHON=ON
  export ARROW_S3=ON
  export ARROW_USE_ASAN=OFF
  export ARROW_USE_CCACHE=ON
  export ARROW_USE_UBSAN=OFF
  export ARROW_WITH_BROTLI=ON
  export ARROW_WITH_BZ2=ON
  export ARROW_WITH_LZ4=ON
  export ARROW_WITH_SNAPPY=ON
  export ARROW_WITH_ZLIB=ON
  export ARROW_WITH_ZSTD=ON
  export ARROW_HOME=$(pwd)
  export GTest_SOURCE=BUNDLED
  export ORC_SOURCE=BUNDLED
  export PARQUET_BUILD_EXAMPLES=ON
  export PARQUET_BUILD_EXECUTABLES=ON
  export PYTHON=python

  ci/scripts/cpp_build.sh $(pwd) $(pwd)
  ci/scripts/python_build.sh $(pwd) $(pwd)

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
  git clone https://github.com/duckdb/duckdb.git

  # now fetch the latest tag to install
  cd duckdb
  git fetch --tags
  latestTag=$(git describe --tags `git rev-list --tags --max-count=1`)
  git checkout $latestTag

  # and then do the install
  cd tools/rpkg
  R -e "remotes::install_deps()"
  DUCKDB_R_EXTENSIONS=tpch R CMD INSTALL .
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
  #source buildkite/benchmark/utils.sh init_conda
  source buildkite/benchmark/utils.sh create_conda_env_with_arrow
  source buildkite/benchmark/utils.sh install_conbench
  python -m buildkite.benchmark.run_benchmark_groups
  #conda deactivate
}

"$@"
