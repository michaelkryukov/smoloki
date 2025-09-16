import asyncio
from unittest.mock import AsyncMock, Mock, patch

import smoloki


class TestPush:
    time_ns = 1673798670922295000
    push_params = {
        "labels": {"service": "web"},
        "information": {"level": "info", "event": "visit", "session": "icfhr9iyu34"},
        "base_endpoint": "host",
    }
    post_payload = {
        "streams": [
            {
                "stream": {
                    "service": "web",
                },
                "values": [
                    [
                        "1673798670922295000",
                        "level=info event=visit session=icfhr9iyu34",
                    ],
                ],
            },
        ],
    }

    def test_push(self):
        with patch("time.time_ns", return_value=self.time_ns):
            with patch(
                "aiohttp.ClientSession.post", new=AsyncMock(return_value=Mock())
            ) as post:
                smoloki.push_sync(
                    **self.push_params,
                )

                post.assert_awaited_once_with(
                    "host/loki/api/v1/push",
                    json=self.post_payload,
                    headers={},
                )

                post.return_value.raise_for_status.assert_called_once()
