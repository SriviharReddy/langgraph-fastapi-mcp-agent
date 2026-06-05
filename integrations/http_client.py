import httpx
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential_jitter,
)


def with_retry(max_attempt=3, max_wait=60):
    return retry(
        stop=stop_after_attempt(max_attempt),
        wait=wait_exponential_jitter(initial=1, max=max_wait),
        reraise=True,
        retry=retry_if_exception_type((httpx.HTTPError, httpx.TimeoutException)),
    )
