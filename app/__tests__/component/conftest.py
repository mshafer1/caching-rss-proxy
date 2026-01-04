import datetime
import functools
import typing

import pytest
import pytest_mock.plugin
import xmltodict

_SAMPLE_DATA = [
    {"id": 1, "value": "A"},
    {"id": 2, "value": "B"},
    {"id": 3, "value": "C"},
]


class RequestsResult:
    def __init__(self, text: str, status_code: int = 200):
        self.text = text
        self.status_code = status_code

    def raise_for_status(self):
        if not (200 <= self.status_code < 300):
            raise Exception(f"HTTP Error: {self.status_code}")

    def text(self):
        return self.text


@functools.total_ordering
class DateComparer:
    def __init__(self, target_date: datetime.date):
        self.target_date = target_date

    def __eq__(self, other: datetime.date) -> bool:
        return all(
            [
                self.target_date.year == other.year,
                self.target_date.month == other.month,
                self.target_date.day == other.day,
            ]
        )

    def __gt__(self, other: datetime.date) -> bool:
        if self.target_date.year != other.year:
            return self.target_date.year > other.year
        return self.target_date.toordinal() > other.toordinal()


@pytest.fixture
def mock_data(mocker: pytest_mock.plugin.MockerFixture) -> typing.Generator[str, None, None]:
    # NOTE: 2006 is chosen because it began on a Sunday, making date calculations easier
    feed_over_time = {
        datetime.date(2006, 1, 1): [_SAMPLE_DATA[0]],
        datetime.date(2006, 1, 2): _SAMPLE_DATA[:2],
        datetime.date(2006, 1, 3): _SAMPLE_DATA[:3],
    }

    def _get_feed():
        now = datetime.datetime.now()  # freezegun will move this
        take = None
        for date_key in feed_over_time:
            if (
                DateComparer(now) >= date_key
            ):  # for some reason, the comparison operators don't work directly on FakeDate
                take = date_key
            if DateComparer(now) < date_key:
                break

        if take is None:
            raise ValueError("No feed data available for this date")

        result = {
            "feed": {"id": "19E428F2-D0FF-4112-AE42-A718218767E0", "entry": feed_over_time[take]}
        }
        return xmltodict.unparse(result)

    mock = mocker.patch("requests.get")
    mock.side_effect = lambda *_, **_kw: RequestsResult(text=_get_feed())

    feed_uri = "https://example.com/test_feed"

    yield feed_uri
