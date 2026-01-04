import re

import flask
import markupsafe
import xmltodict

from caching_rss import _config, _datastore, _rate_limit

APP = flask.Flask(__name__)
APP.config["JSONIFY_SORT_KEYS"] = False
_CACHE = _rate_limit.RateLimitedFeedStore()


@APP.route("/")
def index():
    return "Welcome to the Caching RSS App!"


def _to_bool(value: str) -> bool:
    return value.lower() in {"1", "t", "true"}


def _merge_data_with_stored(data: dict, uri: str) -> dict:
    # assumptions:
    # - new data is sorted newest to oldest
    # - old data is sorted newest to oldest
    # - old data may have items in new data
    # - since both are sorted newest to oldest, we can just prepend new items until we hit an old one
    name = markupsafe.escape(re.sub(r"[^a-zA-Z0-9\.]", "_", uri))
    # TODO: make this configurable
    list_key = "item" if "item" in data.get("rss", {}).get("channel", {}) else "entry"
    list_path = (f"rss/channel/{list_key}" if "rss" in data else f"feed/{list_key}").split("/")

    working_point = data
    for key in list_path[:-1]:
        working_point = working_point.get(key, {})
    items = working_point.get(list_path[-1], [])
    with _datastore.DataStore(name) as store:
        stored_working_point = store
        for key in list_path[:-1]:
            stored_working_point = stored_working_point.get(key, {})
        stored_items = stored_working_point.get(list_path[-1], [])
        # special case, if items is one, make it a list
        if isinstance(items, dict):
            items = [items]
        # merge items
        if not stored_items:
            all_items = items
        else:
            newest_old_items = stored_items[0]
            all_items = []
            for item in items:
                if item == newest_old_items:
                    break
                all_items.append(item)
            all_items.extend(stored_items)

        # enforce max size
        if _config.RSS_MAX_SIZE > 0:
            all_items = all_items[: _config.RSS_MAX_SIZE + 1]

        # bring in the current version of all other fields
        store.clear()
        store.update(data)
        stored_working_point = store
        for key in list_path[:-1]:
            stored_working_point = stored_working_point.get(key, {})
        stored_working_point[list_path[-1]] = all_items
    return store


def _fetch_feed(uri: str, return_json: bool = False) -> flask.Response:
    data = _CACHE.get_feed(uri)
    converted_data = xmltodict.parse(data)
    converted_data = _merge_data_with_stored(converted_data, uri)

    if return_json:
        result = flask.jsonify(converted_data)
    else:
        result = flask.Response(xmltodict.unparse(converted_data), mimetype="application/rss+xml")

    return result


@APP.route("/rss")
def rss_feed():
    feed = flask.request.args.get("feed", "")
    if not feed or feed not in _config.RSS_ALLOWED_FEEDS:
        if APP.config.get("TESTING", False):
            print("Warning, feed not allowed:", feed)
        else:
            return flask.Response("Feed not allowed", status=403)

    return_json = _to_bool(flask.request.args.get("json", "0"))
    return _fetch_feed(feed, return_json=return_json)
