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

## CLI

```text
usage: smoloki [-h] [-b BASE_ENDPOINT] labels information

cli for pushing to loki

positional arguments:
  labels            json-encoded string with labels
  information       json-encoded string with information

options:
  -h, --help        show this help message and exit
  -b BASE_ENDPOINT  base address of loki server
```

## Usage in NodeJS

Install simple wrapper for installed python module:

```bash
# In your project's folder
smoloki-wrappers --install-wrapper-for-nodejs 'node_modules/'
```

Usage is along this lines:

```js
const smoloki = require('smoloki');

// This is an async function executing CLI from previous
// chapter under the hood.
smoloki.push({ service: 'web' }, { level: 'info', event: 'request_completed' });
```

## Implementation details

- Calls to `push` method will never throw. Any exception will just be
    logged using `logging`.
- Keys in labels and information must be strings.
- Values in labels and information must be string, integers or floats.
- If no `base_endpoint` provided (using parameter or env), nothing
    will happen.

## Configuration

- `SMOLOKI_BASE_ENDPOINT` – base address of loki server.
- `SMOLOKI_BASE_LABELS` - base labels that will be added to logs.
- `SMOLOKI_BASE_INFORMATION` - base information that will be added to logs.
