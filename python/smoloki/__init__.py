import asyncio
import json
import logging
import os
import re
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from typing import Set
from typing import Optional, Union
import aiohttp
import requests

SMOLOKI_BASE_ENDPOINT = os.environ.get("SMOLOKI_BASE_ENDPOINT") or ""

SMOLOKI_HEADERS_RAW = os.environ.get("SMOLOKI_HEADERS") or "{}"
SMOLOKI_HEADERS = json.loads(SMOLOKI_HEADERS_RAW)
if not isinstance(SMOLOKI_HEADERS, dict):
    raise ValueError("SMOLOKI_HEADERS should contain JSON object")
if not all([isinstance(value, str) for value in SMOLOKI_HEADERS.values()]):
    raise ValueError("SMOLOKI_HEADERS should contain only strings as values")

SMOLOKI_BASE_LABELS_RAW = os.environ.get("SMOLOKI_BASE_LABELS") or "{}"
SMOLOKI_BASE_LABELS = json.loads(SMOLOKI_BASE_LABELS_RAW)

SMOLOKI_BASE_INFORMATION_RAW = os.environ.get("SMOLOKI_BASE_INFORMATION") or "{}"
SMOLOKI_BASE_INFORMATION = json.loads(SMOLOKI_BASE_INFORMATION_RAW)


def _logfmt_escape(value):
    value = value.replace("\\", "\\\\")
    value = value.replace('"', '\\"')
    value = value.replace("\n", "\\n")
    if " " in value or "=" in value or '"' in value:
        return f'"{value}"'
    return value


def _logfmt_unescape(value):
    if value.startswith('"') and value.endswith('"'):
        value = value[1:-1]
    value = value.replace("\\n", "\n")
    value = value.replace('\\"', '"')
    value = value.replace("\\\\", "\\")
    return value


LOGFMT_PAIR_REGEX = r'(?P<key>\w+)=(?:(?P<rvalue>[^"][^ \n]*)|\"(?P<qvalue>(?:\\.|[^\"])*)\")'


def logfmt_load(data: str) -> dict:
    """
    Read string and return dictionary with values that was formed
    using `logfmt_dump`.
    """
    result = {}
    for match in re.finditer(LOGFMT_PAIR_REGEX, data):
        key = match.group("key")
        value = match.group("rvalue") or match.group("qvalue")
        result[key] = _logfmt_unescape(value)
    return result


def logfmt_dump(data: dict) -> str:
    """
    Return dictionary formatted as "logfmt" string. Can be
    reversed with `logfmt_load`.
    """
    items = []
    for key, value in data.items():
        if not isinstance(key, str):
            raise ValueError("Make sure keys are strings")
        if not key.isidentifier():
            raise ValueError("Make sure keys are valid identifiers")
        if value is None:
            value = ""
        if not isinstance(value, (str, int, float)):
            raise ValueError("Make sure values are strings, integers or floats")
        items.append(f"{key}={_logfmt_escape(str(value))}")
    return " ".join(items)


def _prepare_payload(labels: dict, information: dict) -> dict:
    return {
        "streams": [
            {
                "stream": {
                    **SMOLOKI_BASE_LABELS,
                    **labels,
                },
                "values": [
                    [
                        str(time.time_ns()),
                        logfmt_dump(
                            {
                                **SMOLOKI_BASE_INFORMATION,
                                **information,
                            }
                        ),
                    ],
                ],
            },
        ],
    }


class SmolokiAsyncClient:
    def __init__(
        self,
        base_endpoint: Optional[str] = None,
        headers: Optional[dict] = None,
        trust_env: bool = True,
        timeout: Optional[int] = None,
    ):
        self._base_endpoint = base_endpoint or SMOLOKI_BASE_ENDPOINT
        self._headers = headers or SMOLOKI_HEADERS
        self._trust_env = trust_env
        self._session: Optional[aiohttp.ClientSession] = None
        self._bg_tasks: Set[asyncio.Task] = set()
        self._timeout = timeout or 60

    async def __aenter__(self):
        self._session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=self._timeout),
            trust_env=self._trust_env,
        )
        logging.debug("Created aiohttp session for base_url=%s", self._base_endpoint)
        return self

    async def push(self, labels: dict, information: dict):
        try:
            logging.debug("smoloki POST %s (background=False)", self._base_endpoint)
            response = await self._session.post(
                f"{self._base_endpoint.rstrip('/')}/loki/api/v1/push",
                headers=self._headers,
                json=_prepare_payload(labels, information),
            )
            response.raise_for_status()
        except Exception:
            logging.exception("Error while sending logs with smoloki:")

    async def push_in_background(self, labels: dict, information: dict):
        task = asyncio.create_task(self.push(labels, information))
        self._bg_tasks.add(task)
        task.add_done_callback(lambda t: self._bg_tasks.discard(t))
        logging.debug("Scheduled background push task for %s", self._base_endpoint)

    async def __aexit__(self, exc_type, exc, tb):
        try:
            await asyncio.gather(*list(self._bg_tasks))
            await self._session.close()
        finally:
            self._bg_tasks.clear()


SMOLOKI_WORKERS = int(os.environ.get("SMOLOKI_WORKERS") or 8)

# One module-wide thread pool
_EXECUTOR = ThreadPoolExecutor(max_workers=SMOLOKI_WORKERS, thread_name_prefix="push-sync")
# Per-thread requests.Session for connection reuse and thread-safety
_THREAD_CONTEXT = threading.local()


def _get_session() -> requests.Session:
    sess = getattr(_THREAD_CONTEXT, "session", None)
    if sess is None:
        sess = requests.Session()
        setattr(_THREAD_CONTEXT, "session", sess)
    return sess


def push_sync(
    labels: dict,
    information: dict,
    base_endpoint: Optional[str] = None,
    headers: dict = None,
    timeout: float = 60.0,
    verify: Union[bool, str] = False,
):
    """
    Sends a synchronous POST request to loki.
    - timeout: seconds (float)
    - verify: True/False or a path to a custom CA bundle
    """
    base_endpoint = base_endpoint or SMOLOKI_BASE_ENDPOINT

    if not base_endpoint:
        return

    session = _get_session()

    try:
        resp = session.post(
            f"{base_endpoint.rstrip('/')}/loki/api/v1/push",
            json=_prepare_payload(labels, information),
            headers=headers or SMOLOKI_HEADERS,
            timeout=timeout,
            verify=verify,
        )
        resp.raise_for_status()
    except Exception:
        logging.exception("Error while sending logs with smoloki:")


def push_sync_in_background(
    labels: dict,
    information: dict,
    base_endpoint: Optional[str] = None,
    headers: dict = None,
    timeout: float = 60.0,
    verify: Union[bool, str] = False,
):
    """
    Runs `push_sync` in the background via a shared ThreadPoolExecutor.
    """
    try:
        _EXECUTOR.submit(
            push_sync,
            labels,
            information,
            base_endpoint,
            headers,
            timeout,
            verify,
        )
    except Exception:
        logging.exception("Error while sending logs with smoloki:")
