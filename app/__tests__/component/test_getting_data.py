import flask
import flask.testing
import pytest
import pytest_snapshot.plugin
import xmltodict


@pytest.mark.parametrize(
    "mock_today",
    [
        "2006-01-01",
        "2006-01-02",
        "2006-01-03",
    ],
    ids=lambda d: d,
)
def test___particular_date___fetches_expected_data(
    mock_today: str,
    client: flask.testing.FlaskClient,
    mock_data: str,
    freezer,
    snapshot: pytest_snapshot.plugin.Snapshot,
):
    freezer.move_to(mock_today)

    r = client.get(f"/rss?feed={mock_data}")

    assert r.status_code == 200
    d = xmltodict.parse(r.text)  # implicitly assert a no-throw
    snapshot.assert_match(xmltodict.unparse(d, pretty=True), "expected.xml")

