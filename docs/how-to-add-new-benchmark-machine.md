## How to Add New Benchmark Machine

### 1. Create Pull Request for adding your benchmark machine
- Add your benchmark machine to `MACHINES` in [config.py](../config.py)
```python
MACHINES = {
    "your-benchmark-machine": {
        "info": "langs = Python",
        "default_filters": {
            "arrow-commit": {"lang": "Python"},
        },
        "supported_filters": ["name", "lang"],
        "supported_langs": ["Python"],
        "offline_warning_enabled": False,
    },
}
```
### 2. Get environment vars for Buildkite Agent that will run on your benchmark machine
- Add a comment to your Pull Request
```
@ElenaHenderson Will you please provide environment vars for Buildkite Agent for our benchmark machine 
with name = your-benchmark-machine:
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

### 3. Setup your benchmark machine
- Note that `setup-benchmark-machine-ubuntu-20.04.sh` only installs dependencies for Apache Arrow C++, Python, R, Java and JavaScript.
- If you need to install additional dependencies, please update `setup-benchmark-machine-ubuntu-20.04.sh`. 
- If your machine is running OS other than Ubuntu, please create a new setup script and use `setup-benchmark-machine-ubuntu-20.04.sh` as a reference.

```shell script
sudo su

# Export env vars to be used by setup-benchmark-machine-ubuntu-20.04.sh
export ARROW_BCI_URL=<ARROW_BCI_URL>
export ARROW_BCI_API_ACCESS_TOKEN=<ARROW_BCI_API_ACCESS_TOKEN>
export BUILDKITE_AGENT_TOKEN=<BUILDKITE_AGENT_TOKEN>
export BUILDKITE_QUEUE=<BUILDKITE_QUEUE>
export CONBENCH_EMAIL=<CONBENCH_EMAIL>
export CONBENCH_PASSWORD=<CONBENCH_PASSWORD>
export CONBENCH_URL=<CONBENCH_URL>
export MACHINE=<MACHINE>

# Install Apache Arrow C++, Python, R, Java and JavaScript dependencies and Buildkite Agent
curl -LO https://raw.githubusercontent.com/ursacomputing/arrow-benchmarks-ci/fix-bugs-in-setup-script/scripts/setup-benchmark-machine-ubuntu-20.04.sh
chmod +x setup-benchmark-machine-ubuntu-20.04.sh
source ./setup-benchmark-machine-ubuntu-20.04.sh

# Install Conda for buildkite-agent user
su - buildkite-agent
curl -LO https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
bash Miniconda3-latest-Linux-x86_64.sh -b -p "$HOME/miniconda3"
"$HOME/miniconda3/bin/conda" init
exit

# Start Buildkite Agent
systemctl enable buildkite-agent && systemctl start buildkite-agent

# Verify Buildkite Agent is running
journalctl -f -u buildkite-agent
ps aux | grep buildkite
```
