from unittest.mock import patch, AsyncMock, Mock
import smoloki


def test_push():
    with patch("time.time_ns", return_value=1673798670922295000):
        with patch("aiohttp.ClientSession.post", new=AsyncMock(return_value=Mock())) as post:
            smoloki.push_sync(
                {"service": "web"},
                {"level": "info", "event": "visit", "session": "icfhr9iyu34"},
                base_endpoint="host",
            )

            post.assert_awaited_once_with(
                "host/loki/api/v1/push",
                json={
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
                },
                headers={},
            )

            post.return_value.raise_for_status.assert_called_once()
