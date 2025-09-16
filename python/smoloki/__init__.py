import asyncio
import json
import logging
import os
import re
import time
from typing import Set

import aiohttp

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


def _run_as_sync(future):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    if loop.is_running():
        raise RuntimeError("You have running event loop; sync methods are unavailable")
    loop.run_until_complete(future)


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
        base_endpoint: str | None = None,
        headers: dict | None = None,
        trust_env: bool = True,
        timeout: int | None = None,
    ):
        self._base_endpoint = base_endpoint or SMOLOKI_BASE_ENDPOINT
        self._headers = headers or SMOLOKI_HEADERS
        self._trust_env = trust_env
        self._session: aiohttp.ClientSession | None = None
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
        finally:
            self._bg_tasks.clear()


async def _push(labels, information, base_endpoint=None, headers=None):
    """Push log to loki."""

    base_endpoint = base_endpoint or SMOLOKI_BASE_ENDPOINT

    if not base_endpoint:
        return

    try:
        async with aiohttp.ClientSession(trust_env=True) as session:
            response = await session.post(
                f"{base_endpoint.rstrip('/')}/loki/api/v1/push",
                headers=headers or SMOLOKI_HEADERS,
                json=_prepare_payload(labels, information),
            )
            response.raise_for_status()
    except Exception:
        logging.exception("Error while sending logs with smoloki:")


def push_sync(*args, **kwargs):
    """Push log to loki (synchronously)."""
    return _run_as_sync(_push(*args, **kwargs))
