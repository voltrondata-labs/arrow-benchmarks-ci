#!/bin/bash

echo "-------Installing C++ dependencies"
curl -LO https://raw.githubusercontent.com/apache/arrow/master/cpp/Brewfile
brew update && brew install node && brew bundle --file=Brewfile

echo "-------Installing Buildkite Agent"
brew install buildkite/buildkite/buildkite-agent

echo "-------Setting up Buildkite agent config and hooks"
sed -i '' "s/xxx/$BUILDKITE_AGENT_TOKEN/g" "$(brew --prefix)"/etc/buildkite-agent/buildkite-agent.cfg
echo "tags=\"queue=$BUILDKITE_QUEUE\"" >> "$(brew --prefix)"/etc/buildkite-agent/buildkite-agent.cfg

touch "$(brew --prefix)"/etc/buildkite-agent/hooks/environment
{
  echo "export ARROW_BCI_URL=$ARROW_BCI_URL"
  echo "export ARROW_BCI_API_ACCESS_TOKEN=$ARROW_BCI_API_ACCESS_TOKEN"
  echo "export CONBENCH_EMAIL=$CONBENCH_EMAIL"
  echo "export CONBENCH_PASSWORD=$CONBENCH_PASSWORD"
  echo "export CONBENCH_URL=$CONBENCH_URL"
  echo "export MACHINE=$MACHINE"
  echo "export GITHUB_PAT=$GITHUB_PAT"
} >> "$(brew --prefix)"/etc/buildkite-agent/hooks/environment

echo "-------Setting NOPASSWD for voltrondata user"
echo "voltrondata ALL=(ALL) NOPASSWD:ALL" | sudo tee -a /etc/sudoers
echo "Done"
