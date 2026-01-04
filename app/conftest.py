import pathlib

import flask
import flask.testing
import pytest
import pytest_mock.plugin

import caching_rss


@pytest.fixture(autouse=True)
def app(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch):
    app = caching_rss.APP
    app.config.update({"TESTING": True})

    monkeypatch.chdir(tmp_path)  # ensure isolated data caches
    try:
        yield app
    finally:
        caching_rss._CACHE.clear()


@pytest.fixture()
def client(app: flask.Flask) -> flask.testing.FlaskClient:
    return app.test_client()


@pytest.fixture(autouse=True)
def config(mocker: pytest_mock.plugin.MockerFixture) -> None:
    mocker.patch("caching_rss._config.RSS_ALLOWED_FEEDS", {"https://example.com/test_feed"})
    mocker.patch("caching_rss._config.RSS_MAX_SIZE", 2)
