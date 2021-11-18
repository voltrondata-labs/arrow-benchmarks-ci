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
        r-base \
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

# Install conda so all benchmark build scripts that are run on bare metal in conda env are run
# the same way in the docker container
RUN curl -LO https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
RUN bash Miniconda3-latest-Linux-x86_64.sh -b
ENV PATH="/root/miniconda3/bin:${PATH}"
RUN eval "$(command '/root/miniconda3/bin/conda' 'shell.bash' 'hook' 2> /dev/null)"

# Set Arrow build env vars in Dockerfile so they are available
# to RUN commands during docker build process and docker containers.
# These env vars can only be set by "bash buildkite/benchmark/utils.sh create_conda_env_with_arrow"
# command when it is run outside of docker build process
ENV ARROW_BUILD_TESTS="OFF" \
    ARROW_BUILD_TYPE="release"  \
    ARROW_DEPENDENCY_SOURCE="AUTO"  \
    ARROW_DATASET="ON"  \
    ARROW_DEFAULT_MEMORY_POOL="mimalloc"  \
    ARROW_ENABLE_UNSAFE_MEMORY_ACCESS="true"  \
    ARROW_ENABLE_NULL_CHECK_FOR_GET="false"  \
    ARROW_FLIGHT="OFF"  \
    ARROW_GANDIVA="OFF"  \
    ARROW_HDFS="ON"  \
    ARROW_HOME="/root/miniconda3/envs/arrow-commit"  \
    ARROW_INSTALL_NAME_RPATH="OFF"  \
    ARROW_MIMALLOC="ON"  \
    ARROW_NO_DEPRECATED_API="ON"  \
    ARROW_ORC="ON"  \
    ARROW_PARQUET="ON"  \
    ARROW_PLASMA="ON"  \
    ARROW_PYTHON="ON"  \
    ARROW_S3="ON"  \
    ARROW_USE_ASAN="OFF"  \
    ARROW_USE_CCACHE="ON"  \
    ARROW_USE_UBSAN="OFF"  \
    ARROW_WITH_BROTLI="ON"  \
    ARROW_WITH_BZ2="ON"  \
    ARROW_WITH_LZ4="ON"  \
    ARROW_WITH_SNAPPY="ON"  \
    ARROW_WITH_ZLIB="ON"  \
    ARROW_WITH_ZSTD="ON"  \
    GTest_SOURCE="BUNDLED"  \
    ORC_SOURCE="BUNDLED"  \
    PARQUET_BUILD_EXAMPLES="ON"  \
    PARQUET_BUILD_EXECUTABLES="ON"  \
    PYTHON="python"  \
    LD_LIBRARY_PATH="/root/miniconda3/envs/arrow-commit/lib":$LD_LIBRARY_PATH

# Set benchmark build env vars
ENV ARROW_REPO="https://github.com/apache/arrow.git" \
    BENCHMARKABLE_TYPE="arrow-commit" \
    BENCHMARKABLE="641554b0bcce587549bfcfd0cde3cb4bc23054aa" \
    PYTHON_VERSION="3.8" \
    BENCHMARKS_DATA_DIR="/test"

WORKDIR /build
COPY buildkite/benchmark/utils.sh /build/buildkite/benchmark/utils.sh
RUN bash buildkite/benchmark/utils.sh create_conda_env_with_arrow
RUN bash buildkite/benchmark/utils.sh install_conbench

COPY buildkite/benchmark /build/buildkite/benchmark
COPY utils.py /build/utils.py

ENV FILTERS="{}"
ENV RUN_ID="test1234567"
ENV RUN_NAME="test1234567"
ENV MACHINE="docker-test"
ENV CONBENCH_URL="https://conbench.ursa.dev"
