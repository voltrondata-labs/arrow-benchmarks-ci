#!/bin/bash

init_conda() {
  eval "$(command "$HOME/miniconda3/bin/conda" 'shell.bash' 'hook' 2> /dev/null)"
}

create_conda_env_for_arrow_commit() {
  clone_arrow_repo
  pushd arrow

  conda create -y -n "${BENCHMARKABLE_TYPE}" -c conda-forge \
  --file ci/conda_env_unix.txt \
  --file ci/conda_env_cpp.txt \
  --file ci/conda_env_python.txt \
  compilers \
  python="${PYTHON_VERSION}" \
  pandas \
  r

  source dev/conbench_envs/hooks.sh activate_conda_env_for_benchmark_build
  
  if [[ "$OSTYPE" == "darwin"* ]]
  then
    conda install -c conda-forge aws-sdk-cpp
  else
    conda install -c conda-forge https://anaconda.org/conda-forge/aws-sdk-cpp/1.9.185/download/linux-64/aws-sdk-cpp-1.9.185-h5b750dd_0.tar.bz2
  fi
  
  source dev/conbench_envs/hooks.sh install_arrow_python_dependencies
  source dev/conbench_envs/hooks.sh set_arrow_build_and_run_env_vars

  export RANLIB=`which $RANLIB`
  export AR=`which $AR`
  export ARROW_JEMALLOC=OFF
  export ARROW_ORC=OFF

  source dev/conbench_envs/hooks.sh build_arrow_cpp
  source dev/conbench_envs/hooks.sh build_arrow_python
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

clone_arrow_repo() {
  rm -rf arrow
  git clone "${ARROW_REPO}"
  pushd arrow
  git fetch -v --prune -- origin "${BENCHMARKABLE}"
  git checkout -f "${BENCHMARKABLE}"
  popd
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
  clone_arrow_repo
  pushd arrow
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

test_pyarrow_is_built() {
  echo "------------>Testing pyarrow is built"
  python -c "import pyarrow; print(pyarrow.__version__)"
  echo "------------>End"
}

build_arrow_and_run_benchmark_groups() {
  export ARROW_REPO=https://github.com/apache/arrow.git
  init_conda
  create_conda_env_with_arrow
  test_pyarrow_is_built
  install_conbench
  python -m buildkite.benchmark.run_benchmark_groups
}

"$@"
