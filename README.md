# smoloki

[![PyPI version](https://badge.fury.io/py/smoloki.svg)](https://badge.fury.io/py/smoloki)
[![npm version](https://badge.fury.io/js/smoloki.svg)](https://badge.fury.io/js/smoloki)

Tiny library to push logs to `Grafana Loki` in `logfmt` format.

## CLI

```text
usage: smoloki [-h] [-b BASE_ENDPOINT] [-H HEADERS] labels information

cli for pushing to loki

positional arguments:
  labels            json-encoded string with labels
  information       json-encoded string with information

optional arguments:
  -h, --help        show this help message and exit
  -b BASE_ENDPOINT  base address of loki server
  -H HEADERS        json-encoded string with headers for request to loki server
```

## Usage in Python

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

## Usage in NodeJS

```js
const smoloki = require('smoloki');

async function as_request_completed() {
    await smoloki.push({ service: 'web' }, { level: 'info', event: 'request_completed' });
}
```

## Implementation details

- Calls to `push` method will never throw. Any exception will just be
    logged using `logging`.
- Keys in labels and information must be strings. If `None` is provided as
    value in case of python, it will be serialized as empty string.
- Values in labels and information must be string, integers or floats.
- If no `base_endpoint` provided (using parameter or env), nothing will happen.

## Configuration

- `SMOLOKI_BASE_ENDPOINT` – base address of loki server.
- `SMOLOKI_HEADERS` - headers for request to loki server (can be used for authorization).
- `SMOLOKI_BASE_LABELS` - base labels that will be added to logs.
- `SMOLOKI_BASE_INFORMATION` - base information that will be added to logs.
