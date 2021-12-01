## How to Add New Benchmark Machine

Note that we only have a script for setting up benchmark machine with Ubuntu 20.04.2 x86_64 GNU/Linux.

### 1. Get environment vars for Buildkite Agent that will run on your benchmark machine
- Create [new issue](https://github.com/ursacomputing/arrow-benchmarks-ci/issues/new) with a comment like this:
```
@ElenaHenderson We want to add a new benchmark machine with name = your-machine-name that will be 
running Rust/Java/etc benchmarks and we need these Buildkite environment vars:
- ARROW_BCI_URL
- ARROW_BCI_API_ACCESS_TOKEN
- BUILDKITE_AGENT_TOKEN
- BUILDKITE_QUEUE
- CONBENCH_EMAIL
- CONBENCH_PASSWORD
- CONBENCH_URL
- MACHINE
```
- Please also let us know how you would like environment vars to be shared with you.

### 2. Run setup-benchmark-machine-ubuntu-20.04.sh script on your benchmark machine
```shell script
sudo su
git clone https://github.com/ursacomputing/arrow-benchmarks-ci.git
cd arrow-benchmarks-ci/

export ARROW_BCI_URL=<ARROW_BCI_URL>
export ARROW_BCI_API_ACCESS_TOKEN=<ARROW_BCI_API_ACCESS_TOKEN>
export BUILDKITE_AGENT_TOKEN=<BUILDKITE_AGENT_TOKEN>
export BUILDKITE_QUEUE=<BUILDKITE_QUEUE>
export CONBENCH_EMAIL=<CONBENCH_EMAIL>
export CONBENCH_PASSWORD=<CONBENCH_PASSWORD>
export CONBENCH_URL=<CONBENCH_URL>
export MACHINE=<MACHINE>

source ./scripts/setup-benchmark-machine-ubuntu-20.04.sh
```
