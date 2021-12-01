## Admin Tasks

Admin Tasks can only performed by a contributor who has access to AWS account running Arrow Benchmarks CI and 
Apache Arrow Buildkite Org

### Create ARROW_BCI_API_ACCESS_TOKEN for Benchmark Machine
```shell script
kubectl exec -it deploy/arrow-bci-deployment bash
root@arrow-bci-deployment-75f67db476-vcth8:/app# python
Python 3.8.12 (default, Oct 13 2021, 09:15:35) 
[GCC 10.2.1 20210110] on linux
Type "help", "copyright", "credits" or "license" for more information.
>>> from models.machine import Machine
>>> Machine(name='new-machine').create_api_access_token()
```

### Create BUILDKITE_AGENT_TOKEN for Benchmark Machine
- Go to https://buildkite.com/organizations/apache-arrow/settings
- Copy Organization ID under GraphQL API Integration so you can use it in the next step
- Go to https://buildkite.com/user/graphql/console
- Paste this query
```
mutation {
  agentTokenCreate(input: {
    organizationID: "Organization ID",
    description: "BK agent token for Benchmark Machine X"
  }) {
    agentTokenEdge {
      node {
        id
        token
      }
    }
  }
}
```  
- click Execute
- Copy token from results
```
{
  "data": {
    "agentTokenCreate": {
      "agentTokenEdge": {
        "node": {
          "id": "xxx",
          "token": "copy-this-value"
        }
      }
    }
  }
}
```

### Create CONBENCH_EMAIL and CONBENCH_PASSWORD for Benchmark Machine
- Go to https://conbench.ursa.dev/register/ and add new user
