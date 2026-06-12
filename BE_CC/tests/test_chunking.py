import pytest
from app.services.ingestion_service import _chunk_text, _deterministic_id, _extract_text


def test_chunk_text_basic():
    words = ["word"] * 600
    text = " ".join(words)
    chunks = _chunk_text(text, chunk_size=500, overlap=50)
    assert len(chunks) >= 2
    for chunk in chunks:
        assert len(chunk) >= 50


def test_chunk_text_discards_short():
    chunks = _chunk_text("short", chunk_size=500, overlap=50)
    assert chunks == []


def test_chunk_text_overlap():
    words = [str(i) for i in range(1000)]
    text = " ".join(words)
    chunks = _chunk_text(text, chunk_size=100, overlap=20)
    first_words = chunks[0].split()[-20:]
    second_words = chunks[1].split()[:20]
    assert first_words == second_words


def test_deterministic_id_stable():
    id1 = _deterministic_id("https://example.com", "some text")
    id2 = _deterministic_id("https://example.com", "some text")
    assert id1 == id2


def test_deterministic_id_unique():
    id1 = _deterministic_id("https://example.com", "text A")
    id2 = _deterministic_id("https://example.com", "text B")
    assert id1 != id2


def test_extract_text_strips_script_and_style():
    html = """
    <html><body>
      <script>var x = 1;</script>
      <style>.foo { color: red; }</style>
      <p>Visible content here.</p>
    </body></html>
    """
    text = _extract_text(html)
    assert "Visible content here." in text
    assert "var x" not in text
    assert ".foo" not in text


def test_extract_text_strips_nav_footer():
    html = """
    <html><body>
      <nav>Nav links</nav>
      <footer>Footer stuff</footer>
      <article>Real article text.</article>
    </body></html>
    """
    text = _extract_text(html)
    assert "Real article text." in text
    assert "Nav links" not in text
    assert "Footer stuff" not in text
