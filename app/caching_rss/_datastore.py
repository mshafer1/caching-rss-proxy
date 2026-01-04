import os.path
import pickle
import logging

from caching_rss import _config

_logger = logging.getLogger(__name__)
_logger.addHandler(logging.NullHandler())

class DataStore:
    def __init__(self, name: str):
        self._data = None
        self._name = name
        self._filename = os.path.join(_config.RSS_STORAGE_PATH, f"{name}.dat")

    @property
    def data(self):
        return self._data

    @property
    def name(self):
        return self._name

    def _load(self):
        if not os.path.exists(self._filename):
            _logger.info("Loading blank for feed")
            self._data = {}
            return

        try:
            _logger.info("Loading data file for feed")
            with open(self._filename, "rb") as f:
                self._data = pickle.load(f)
        except Exception:
            _logger.info("Failed to load data file, setting to empty data")
            self._data = {}

    def __enter__(self):
        self._load()
        return self.data

    def __exit__(self, exc_type, exc_value, traceback):
        with open(self._filename, "wb") as f:
            pickle.dump(self._data, f)
