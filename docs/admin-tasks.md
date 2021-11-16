## Admin Tasks

Admin Tasks can only performed by a contributor who has access to k8s cluster running Arrow Benchmarks CI

### Generate API Access Token for Benchmark Machine
API Access Token can be generated after machine is added to [config.py](../config.py)

    kubectl exec -it deploy/arrow-bci-deployment bash
    root@arrow-bci-deployment-75f67db476-vcth8:/app# python
    Python 3.8.12 (default, Oct 13 2021, 09:15:35) 
    [GCC 10.2.1 20210110] on linux
    Type "help", "copyright", "credits" or "license" for more information.
    >>> from models.machine import Machine
    >>> Machine.get("ursa-i9-9960x").generate_api_access_token()

