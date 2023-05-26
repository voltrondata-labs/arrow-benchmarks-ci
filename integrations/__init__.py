from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

from config import Config
from logger import log

# Note(JP): some requests are known to be responded to within O(1 min).
# Set a large read timeout, but keep connect timeout smaller.
# Also see
# https://github.com/conbench/conbench/issues/801
# https://github.com/conbench/conbench/issues/1283
DEFAULT_TIMEOUT = (10, 180)

retry_strategy = Retry(
    # keep retrying a little longer to survive smaller outages.
    # Also see https://github.com/conbench/conbench/issues/800.
    total=20,
    status_forcelist=[502, 503, 504],
    allowed_methods=frozenset(["GET", "POST"]),
    backoff_factor=4,  # will retry in 2, 4, 8, 16, 32 seconds
)


class IntegrationException(Exception):
    pass


class IntegrationHTTPAdapter(HTTPAdapter):
    def __init__(self, *args, **kwargs):
        self.timeout = DEFAULT_TIMEOUT
        if "timeout" in kwargs:
            self.timeout = kwargs["timeout"]
            del kwargs["timeout"]
        super().__init__(*args, **kwargs)

    def send(self, request, **kwargs):
        timeout = kwargs.get("timeout")
        if timeout is None:
            kwargs["timeout"] = self.timeout
        log.info(f"send: {request.method} {request.url}")

        response = super().send(request, **kwargs)

        if response.status_code < 200 or response.status_code > 399:
            log.error(f"reply: {response.status_code} {response.content}")
            raise IntegrationException(
                f"{request.url} {response.status_code} {response.content}"
            )
        else:
            log.info(f"reply: {response.status_code}")

        return response


class TestIntegrationHTTPAdapter(IntegrationHTTPAdapter):
    def send(self, request, **kwargs):
        from tests.helpers import outbound_requests

        outbound_requests.append((request.url, request.body))

        return super().send(request, **kwargs)


if Config.ENV == "DEV":
    adapter = TestIntegrationHTTPAdapter(max_retries=retry_strategy)
else:
    adapter = IntegrationHTTPAdapter(max_retries=retry_strategy)
