# Test Env

Test env is used for testing APIs and CI scripts with mocked Buildkite, Github, Pypy, Slack and Conbench.

## Run tests
```shell script
docker-compose -f envs/test/docker-compose.yml down
docker-compose -f envs/test/docker-compose.yml build
docker-compose -f envs/test/docker-compose.yml run app pytest -vv tests/
```
