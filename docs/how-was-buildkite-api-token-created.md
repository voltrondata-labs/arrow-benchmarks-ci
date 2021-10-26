## How was `BUILDKITE_API_TOKEN` created

1. Go to https://buildkite.com/user/api-access-tokens/new
- Description = arrow-benchmarks-ci
- Organization Access - select your org
- Under REST API Scopes, select:
    - `Read Builds`
    - `Modify Builds`
    - `Read Pipelines`
    - `Write Pipelines`
- click Create New API Access Token
- copy token and use it for `BUILDKITE_API_TOKEN`
