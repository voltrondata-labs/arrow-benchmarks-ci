FROM ubuntu:20.04

RUN apt-get -y update
RUN apt-get -y upgrade
RUN apt-get install python3 -y
RUN apt-get install python3-pip -y
RUN apt-get install -y -q curl
RUN curl -LO https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
RUN bash Miniconda3-latest-Linux-x86_64.sh -b

ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get install -y -q --no-install-recommends \
    autoconf \
    ca-certificates \
    ccache \
    cmake \
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
    ninja-build \
    pkg-config \
    protobuf-compiler \
    rapidjson-dev \
    tzdata \
    wget && \
apt-get clean && \
rm -rf /var/lib/apt/lists*

RUN apt-get install -y -q \
    python3 \
    python3-pip \
    python3-dev && \
apt-get clean && \
rm -rf /var/lib/apt/lists/*

RUN apt update && apt -y upgrade
RUN apt -y install curl dirmngr apt-transport-https lsb-release ca-certificates
RUN curl -fsSL https://deb.nodesource.com/setup_14.x
RUN apt-get install -y -q nodejs
RUN apt install -y -q yarn
RUN apt install -y -q gcc g++ make

WORKDIR /build

ENV ARROW_REPO=https://github.com/apache/arrow.git
ENV BENCHMARKABLE_TYPE="arrow-commit"
ENV BENCHMARKABLE="b305edb2db9177e1a2b56a7713bfe49259315961"
ENV PYTHON_VERSION="3.8"
ENV BENCHMARKS_DATA_DIR="/test"
ENV PATH="/root/miniconda3/bin:${PATH}"
COPY buildkite/benchmark/utils.sh /build/buildkite/benchmark/utils.sh
RUN bash buildkite/benchmark/utils.sh create_conda_env_with_arrow
RUN bash buildkite/benchmark/utils.sh install_conbench
ENV FILTERS="{\"name\":\"dataset-select\"}"
COPY buildkite/benchmark /build/buildkite/benchmark
COPY utils.py /build/utils.py
