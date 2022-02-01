#!/bin/bash

init_conda() {
  if [ -d "/var/lib/buildkite-agent" ]; then
    eval "$(command '/var/lib/buildkite-agent/miniconda3/bin/conda' 'shell.bash' 'hook' 2> /dev/null)"
  else
    eval "$(command '/root/miniconda3/bin/conda' 'shell.bash' 'hook' 2> /dev/null)"
  fi
}

create_conda_env_for_arrow_commit() {
  clone_arrow_repo
  pushd arrow
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

create_virtualenv_with_arrow() {
  virtualenv venv --python="${PYTHON_VERSION}"
  source venv/bin/activate
  clone_arrow_repo
  pushd arrow
  source dev/conbench_envs/hooks.sh install_arrow_python_dependencies
  export CONDA_PREFIX="$(brew --prefix)"/dist
  source dev/conbench_envs/hooks.sh set_arrow_build_and_run_env_vars
#  export ARROW_HOME=$(pwd)
#  export LD_LIBRARY_PATH=$ARROW_HOME/lib
  source dev/conbench_envs/hooks.sh build_arrow_cpp
  source dev/conbench_envs/hooks.sh build_arrow_python
  echo "------------>test"
  python -c "import pyarrow; import pyarrow.dataset as ds; pyarrow.__version__"
  echo "------------> end test"
  popd
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
  echo "------------>test"
  python -c "import pyarrow; import pyarrow.dataset as ds; pyarrow.__version__"
  echo "------------> end test"
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
  echo "------------>test before archery"
  python -c "import pyarrow; import pyarrow.dataset as ds; print(pyarrow.__version__)"
  echo "------------> end test"
  clone_arrow_repo
  pushd arrow
  source dev/conbench_envs/hooks.sh install_archery
  popd
  echo "------------>test after archery"
  python -c "print('here'); import pyarrow; import pyarrow.dataset as ds; print(pyarrow.__version__)"
  echo "------------> end test"
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

  case "$(uname)" in
    Linux)
      init_conda
      create_conda_env_with_arrow
      ;;
    Darwin)
      create_virtualenv_with_arrow
      ;;
    *)
      echo "buildkite/benchmark/utils.sh supports only building Arrow and running benchmarks on Linux and MacOS. Please update this script to work for your machine's OS"
      exit 1
      ;;
  esac

  install_conbench
  python -m buildkite.benchmark.run_benchmark_groups
}

"$@"
