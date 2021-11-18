FROM ubuntu:20.04

ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update -y -q && \
    apt-get install -y -q \
        python3 \
        python3-pip \
        python3-dev && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Install C++, Java and R dependencies
ARG r=4.1
ARG jdk=8
RUN apt-get update -y -q && \
    apt-get install -y -q --no-install-recommends \
        autoconf \
        ca-certificates \
        ccache \
        cmake \
        curl \
        g++ \
        gcc \
        gdb \
        git \
        libbenchmark-dev \
        libboost-filesystem-dev \
        libboost-regex-dev \
        libboost-system-dev \
        libbrotli-dev \
        libbz2-dev \
        libgflags-dev \
        libcurl4-openssl-dev \
        libgoogle-glog-dev \
        liblz4-dev \
        libprotobuf-dev \
        libprotoc-dev \
        libre2-dev \
        libsnappy-dev \
        libssl-dev \
        libthrift-dev \
        libutf8proc-dev \
        libzstd-dev \
        make \
        maven \
        ninja-build \
        openjdk-${jdk}-jdk \
        pkg-config \
        protobuf-compiler \
        rapidjson-dev \
        r-recommended=${r}* \
        r-base=${r}* \
        tzdata \
        wget && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists*

# Install JavaScript dependencies
ARG node=14
RUN apt-get update -y -q && \
    wget -q -O - https://deb.nodesource.com/setup_${node}.x | bash - && \
    apt-get install -y nodejs && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* && \
    npm install -g yarn

# Install conda so all benchmark build scripts that run on bare metal in conda env are run
# the same way in docker container
RUN curl -LO https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
RUN bash Miniconda3-latest-Linux-x86_64.sh -b
ENV PATH="/root/miniconda3/bin:${PATH}"
RUN eval "$(command '/root/miniconda3/bin/conda' 'shell.bash' 'hook' 2> /dev/null)"

# Set Arrow build env vars in Dockerfile so they are available
# to RUN commands during docker build process and docker containers.
# These env vars can only be set by "bash buildkite/benchmark/utils.sh create_conda_env_with_arrow"
# command when it is run outside of docker build process
ENV ARROW_BUILD_TESTS="OFF"
ENV ARROW_BUILD_TYPE="release"
ENV ARROW_DEPENDENCY_SOURCE="AUTO"
ENV ARROW_DATASET="ON"
ENV ARROW_DEFAULT_MEMORY_POOL="mimalloc"
ENV ARROW_ENABLE_UNSAFE_MEMORY_ACCESS="true"
ENV ARROW_ENABLE_NULL_CHECK_FOR_GET="false"
ENV ARROW_FLIGHT="OFF"
ENV ARROW_GANDIVA="OFF"
ENV ARROW_HDFS="ON"
ENV ARROW_HOME="/root/miniconda3/envs/arrow-commit"
ENV ARROW_INSTALL_NAME_RPATH="OFF"
ENV ARROW_MIMALLOC="ON"
ENV ARROW_NO_DEPRECATED_API="ON"
ENV ARROW_ORC="ON"
ENV ARROW_PARQUET="ON"
ENV ARROW_PLASMA="ON"
ENV ARROW_PYTHON="ON"
ENV ARROW_S3="ON"
ENV ARROW_USE_ASAN="OFF"
ENV ARROW_USE_CCACHE="ON"
ENV ARROW_USE_UBSAN="OFF"
ENV ARROW_WITH_BROTLI="ON"
ENV ARROW_WITH_BZ2="ON"
ENV ARROW_WITH_LZ4="ON"
ENV ARROW_WITH_SNAPPY="ON"
ENV ARROW_WITH_ZLIB="ON"
ENV ARROW_WITH_ZSTD="ON"
ENV GTest_SOURCE="BUNDLED"
ENV ORC_SOURCE="BUNDLED"
ENV PARQUET_BUILD_EXAMPLES="ON"
ENV PARQUET_BUILD_EXECUTABLES="ON"
ENV PYTHON="python"
ENV LD_LIBRARY_PATH="/root/miniconda3/envs/arrow-commit/lib":$LD_LIBRARY_PATH

# Set benchmark build env vars
ENV ARROW_REPO="https://github.com/apache/arrow.git"
ENV BENCHMARKABLE_TYPE="arrow-commit"
ENV BENCHMARKABLE="b305edb2db9177e1a2b56a7713bfe49259315961"
ENV PYTHON_VERSION="3.8"
ENV BENCHMARKS_DATA_DIR="/test"

WORKDIR /build
COPY buildkite/benchmark/utils.sh /build/buildkite/benchmark/utils.sh
RUN bash buildkite/benchmark/utils.sh create_conda_env_with_arrow
RUN bash buildkite/benchmark/utils.sh install_conbench

COPY buildkite/benchmark /build/buildkite/benchmark
COPY utils.py /build/utils.py

ENV FILTERS="{}"
ENV RUN_ID="test123456"
ENV RUN_NAME="test123456"
ENV MACHINE="docker-test"
ENV CONBENCH_URL="https://conbench.ursa.dev"
