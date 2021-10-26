from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

from logger import log

DEFAULT_TIMEOUT = 30

retry_strategy = Retry(
    total=5,
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


adapter = IntegrationHTTPAdapter(max_retries=retry_strategy)
