import typing

import flask.testing
import pytest

import caching_rss


def get_time_series(
    freezer, day_base: str, get_feed: typing.Callable[[], None]
) -> typing.List[typing.Tuple[str, int, int]]:
    test_data = []

    for time in [
        "00:00:00",
        "00:10:00",
        "00:59:00",
        "01:00:00",
        "01:30:00",
        "02:00:00",
    ]:
        freezer.move_to(day_base + time)
        get_feed()
        info = caching_rss._CACHE.cache_info
        test_data.append((time, info.hits, info.misses))
    return test_data


def test___time__query___hits_cache_expected_frequency(
    client: flask.testing.FlaskClient,
    mock_data: str,
    freezer,
):
    day_base = "2006-01-01 "

    test_data = get_time_series(
        freezer, day_base, get_feed=lambda: client.get(f"/rss?feed={mock_data}")
    )

    assert test_data == [
        ("00:00:00", 0, 1),
        ("00:10:00", 1, 1),
        ("00:59:00", 2, 1),
        ("01:00:00", 2, 2),
        ("01:30:00", 3, 2),
        ("02:00:00", 3, 3),
    ]


def test___time___query___cache_is_specific_to_feed(
    client: flask.testing.FlaskClient,
    mock_data: str,
    freezer,
):
    day_base = "2006-01-01 "
    feed2 = "https://example.com/another_feed"
    get_time_series(freezer, day_base, get_feed=lambda: client.get(f"/rss?feed={mock_data}"))

    test_data = get_time_series(
        freezer, day_base, get_feed=lambda: client.get(f"/rss?feed={feed2}")
    )

    assert test_data == [
        ("00:00:00", 3, 4),
        ("00:10:00", 4, 4),
        ("00:59:00", 5, 4),
        ("01:00:00", 5, 5),
        ("01:30:00", 6, 5),
        ("02:00:00", 6, 6),
    ]
