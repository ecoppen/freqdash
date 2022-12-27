import unittest

import responses
from freezegun import freeze_time

from freqdash.core.utils import (
    BlankResponse,
    HTTPRequestError,
    end_datetime_ago,
    end_milliseconds_ago,
    send_public_request,
    start_datetime_ago,
    start_milliseconds_ago,
)


class TestUtils(unittest.TestCase):
    def test_BlankResponse(self):
        blank = BlankResponse()
        assert blank.content == ""

    @freeze_time("2022-12-25")
    def test_start_datetime_ago(self):
        assert start_datetime_ago(5) == "2022-12-20 00:00:00"

    @freeze_time("2022-12-25")
    def test_end_datetime_ago(self):
        assert end_datetime_ago(5) == "2022-12-20 23:59:59"

    @freeze_time("2022-12-25")
    def test_start_milliseconds_ago(self):
        assert start_milliseconds_ago(5) == 1671494400000

    @freeze_time("2022-12-25")
    def test_end_millseconds_ago(self):
        assert end_milliseconds_ago(5) == 1671580799999

    @responses.activate
    def test_HTTPRequestError(self):
        responses.get(
            url="http://api.freqdash.com/error",
            body='{"code": "429", "msg": "Rate limited"}',
            status=200,
            content_type="application/json",
            headers={"X-MBX-USED-WEIGHT-1M": "1"},
        )
        with self.assertRaises(HTTPRequestError) as cm:
            send_public_request(url="http://api.freqdash.com/", url_path="error")
            self.assertEqual(
                "Request to 'http://api.freqdash.com/error' failed. Code: 429; Message: Rate limited",
                str(cm.exception),
            )


if __name__ == "__main__":
    unittest.main()
