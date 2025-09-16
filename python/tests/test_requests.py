from unittest.mock import patch, Mock
import smoloki


def test_push():
    with patch("time.time_ns", return_value=1673798670922295000):
        mock_resp = Mock()
        mock_resp.raise_for_status = Mock(return_value=200)
        mock_post = Mock(return_value=mock_resp)
        with patch("requests.Session.post", new=mock_post) as post:
            smoloki.push_sync(
                {"service": "web"},
                {"level": "info", "event": "visit", "session": "icfhr9iyu34"},
                base_endpoint="host",
            )

            post.assert_called_once_with(
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
                timeout=60,
                verify=False,
            )

            post.return_value.raise_for_status.assert_called_once()
