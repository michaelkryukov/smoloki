import argparse
import json

from . import push_sync


def main():
    parser = argparse.ArgumentParser(
        "smoloki",
        description="cli for pushing to loki",
    )
    parser.add_argument(
        dest="labels",
        type=str,
        help="json-encoded string with labels",
    )
    parser.add_argument(
        dest="information",
        type=str,
        help="json-encoded string with information",
    )
    parser.add_argument(
        "-b",
        dest="base_endpoint",
        type=str,
        default="",
        help="base address of loki server",
    )
    parser.add_argument(
        "-H",
        dest="headers",
        type=str,
        default="{}",
        help="json-encoded string with headers for request to loki server",
    )

    args = parser.parse_args()

    try:
        labels = json.loads(args.labels)
    except json.JSONDecodeError:
        raise ValueError('Value of "labels" is invalid!')

    try:
        information = json.loads(args.information)
    except json.JSONDecodeError:
        raise ValueError('Value of "information" is invalid!')

    try:
        headers = json.loads(args.headers)
    except json.JSONDecodeError:
        raise ValueError('Value of "headers" is invalid!')

    push_sync(
        labels,
        information,
        base_endpoint=args.base_endpoint,
        headers=headers,
    )


if __name__ == "__main__":
    main()
