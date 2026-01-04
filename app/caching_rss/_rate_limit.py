import time
import typing
import logging

import requests

_logger = logging.getLogger(__name__)
_logger.addHandler(logging.NullHandler())


class CacheInfo(typing.NamedTuple):
    hits: int
    misses: int

def _get_ttl_bin(seconds=3600):
    """Return the same value within `seconds` time period"""
    return int(time.time() // seconds)  # integer division seems to yield a .0 float sometimes


class RateLimitedFeedStore:
    def __init__(self):
        self._data = {}
        self._cache_hit = 0
        self._cache_miss = 0

    @property
    def cache_info(self):
        return CacheInfo(self._cache_hit, self._cache_miss)

    def clear(self):
        self._data.clear()
        self._cache_hit = 0
        self._cache_miss = 0

    def _fetch(self, uri):
        r = requests.get(uri, timeout=10)
        r.raise_for_status()
        return r.text

    def get_feed(self, uri: str):
        current_bin = _get_ttl_bin()
        if uri not in self._data:
            self._cache_miss += 1
            _logger.info("Fetching RSS from upstream...")
            result = self._fetch(uri)
            self._data[uri] = (current_bin, result)
            return result

        ttl_bin, cached = self._data[uri]
        if ttl_bin == current_bin:
            _logger.info("Returning memory cached RSS feed...")
            self._cache_hit += 1
            return cached
        else:
            _logger.info("Fetching RSS from upstream...")
            self._cache_miss += 1
            result = self._fetch(uri)
            self._data[uri] = (current_bin, result)
            return result
