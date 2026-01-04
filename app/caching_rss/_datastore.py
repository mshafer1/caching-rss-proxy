import os.path
import pickle


class DataStore:
    def __init__(self, name: str):
        self._data = None
        self._name = name
        self._filename = f"{name}.dat"

    @property
    def data(self):
        return self._data

    @property
    def name(self):
        return self._name

    def _load(self):
        if not os.path.exists(self._filename):
            self._data = {}
            return

        try:
            with open(self._filename, "rb") as f:
                self._data = pickle.load(f)
        except Exception:
            self._data = {}

    def __enter__(self):
        self._load()
        return self.data

    def __exit__(self, exc_type, exc_value, traceback):
        with open(self._filename, "wb") as f:
            pickle.dump(self._data, f)
