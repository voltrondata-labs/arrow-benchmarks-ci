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
WORKDIR /build
COPY buildkite/benchmark/utils.sh /build/buildkite/benchmark/utils.sh
COPY buildkite/benchmark /build/buildkite/benchmark
COPY utils.py /build/utils.py
COPY buildkite/benchmark-test/run.sh /build/buildkite/benchmark-test/run.sh
