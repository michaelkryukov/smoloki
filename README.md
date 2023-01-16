# smoloki

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

This library uses `LOKI_BASE_ENDPOINT` environment variable to acquire
base address for requests.
