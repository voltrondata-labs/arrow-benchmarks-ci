FROM ubuntu:20.04

ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get upgrade

# Install C++ dependencies
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
        ninja-build \
        pkg-config \
        protobuf-compiler \
        rapidjson-dev \
        tzdata \
        wget && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists*

# Install Python dependencies
RUN apt-get update -y -q && \
    apt-get install -y -q \
        python3 \
        python3-pip \
        python3-dev && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Install R dependencies
RUN apt-get update -y -q && \
    apt-get install -y -q --no-install-recommends r-base && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists*

# Install JavaScript dependencies
RUN apt-get update -y -q && \
    wget -q -O - https://deb.nodesource.com/setup_14.x | bash - && \
    apt-get install -y nodejs && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists* && \
    npm install -g yarn

# Install Java dependencies
RUN apt-get update -y -q && \
    apt-get install -y -q --no-install-recommends openjdk-8-jdk maven && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists*
RUN update-java-alternatives -s java-1.8.0-openjdk-amd64

# Since this docker image is used for testing benchmark builds that are run on bare metal in conda env,
# install Conda so all benchmark build scripts are run the same way in the docker container
RUN curl -LO https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
RUN bash Miniconda3-latest-Linux-x86_64.sh -b

# Copy files necessary for running bencmarks
WORKDIR /build
COPY buildkite/benchmark /build/buildkite/benchmark
COPY utils.py /build/utils.py
