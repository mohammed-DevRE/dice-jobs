from app.collector import normalize_url


def test_normalize_url_removes_tracking():
    assert normalize_url("HTTPS://Example.COM/jobs/1/?trk=x#top") == "https://example.com/jobs/1"

