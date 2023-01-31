import os
import re
import json
import time
import asyncio
import aiohttp
import logging


SMOLOKI_BASE_ENDPOINT_RAW = os.environ.get("SMOLOKI_BASE_ENDPOINT") or ""
SMOLOKI_BASE_ENDPOINT = SMOLOKI_BASE_ENDPOINT_RAW

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


LOGFMT_PAIR_REGEX = (
    r'(?P<key>\w+)=(?:(?P<rvalue>[^"][^ \n]*)|\"(?P<qvalue>(?:\\.|[^\"])*)\")'
)


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
        if not isinstance(value, (str, int, float)):
            raise ValueError("Make sure values are strings, integers or floats")
        items.append(f"{key}={_logfmt_escape(str(value))}")
    return " ".join(items)


async def request(method, endpoint, base_endpoint=None, **kwargs):
    """Perform some request to loki endpoint."""

    base_endpoint = base_endpoint or SMOLOKI_BASE_ENDPOINT

    async with aiohttp.ClientSession() as session:
        async with session.request(
            method,
            f"{base_endpoint.rstrip('/')}{endpoint}",
            params=kwargs,
        ) as response:
            return await response.json()


def request_sync(*args, **kwargs):
    """Perform some request to loki endpoint (synchronously)."""
    _run_as_sync(request(*args, **kwargs))


async def push(labels, information, base_endpoint=None):
    """Push log to loki."""

    base_endpoint = base_endpoint or SMOLOKI_BASE_ENDPOINT

    if not base_endpoint:
        logging.warning("No 'base_endpoint' configured for smoloki")
        return

    try:
        async with aiohttp.ClientSession() as session:
            response = await session.post(
                f"{base_endpoint.rstrip('/')}/loki/api/v1/push",
                json={
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
                },
            )
            response.raise_for_status()
    except Exception:
        logging.exception("Error while sending logs with smoloki:")


def push_sync(*args, **kwargs):
    """Push log to loki (synchronously)."""
    _run_as_sync(push(*args, **kwargs))
