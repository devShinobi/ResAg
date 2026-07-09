from resag.springer import extract_text_from_html, fetch_paper_text


def test_extract_text_from_html():
    html = """
    <html><body>
    <article>
      <h1>Fraud detection in insurance claims</h1>
      <p>Machine learning improves detection.</p>
      <p>It identifies suspicious patterns in claims data.</p>
    </article>
    </body></html>
    """

    text = extract_text_from_html(html)

    assert "Fraud detection in insurance claims" in text
    assert "Machine learning improves detection." in text
    assert "It identifies suspicious patterns in claims data." in text


def test_fetch_paper_text(monkeypatch):
    class FakeResponse:
        def __init__(self, data: bytes):
            self._data = data

        def read(self) -> bytes:
            return self._data

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

    def fake_urlopen(request, timeout=30):
        assert request.full_url == "https://example.com/paper"
        return FakeResponse(b"<html><body><p>Paper body text</p></body></html>")

    monkeypatch.setattr("resag.springer.urlopen", fake_urlopen)
    text = fetch_paper_text("https://example.com/paper")

    assert "Paper body text" in text
