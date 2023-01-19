# smoloki

[![PyPI version](https://badge.fury.io/py/smoloki.svg)](https://badge.fury.io/py/smoloki)

Tiny library to push logs to `Grafana Loki` in `logfmt` format.

```py
import smoloki


async def as_request_completed():
    await smoloki.push(
        {'service': 'web'},
        {'level': 'info', 'event': 'request_completed'},
    )


def as_request_completed():
    smoloki.push_sync(
        {'service': 'web'},
        {'level': 'info', 'event': 'request_completed'},
    )
```

## Configuration

- `SMOLOKI_BASE_ENDPOINT` – base address of Loki server.
- `SMOLOKI_BASE_LABELS` - base labels that will be added to logs.
- `SMOLOKI_BASE_INFORMATION` - base information that will be added to logs.
