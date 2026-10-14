import pytest
from src.chunking import chunk_pages
from src.config import SOURCES
from src.ingestion import Crawler, IngestionError, extract_page


def test_table_rows_preserve_labels_and_currency():
    html = '<h1>Adrenal package</h1><main class="article-dt-desc"><h2>Costs</h2><table><tr><th>Program</th><th>Cost (USD)</th></tr><tr><td>Outpatient</td><td>$18,995</td></tr><tr><td>Inpatient</td><td>$30,000</td></tr></table><p>' + 'Source description. '*30 + '</p></main>'
    page = extract_page(html, SOURCES[2])
    rows = [b['text'] for b in page['blocks'] if b['kind'] == 'table_row']
    assert rows == ['Program: Outpatient | Cost (USD): $18,995','Program: Inpatient | Cost (USD): $30,000']
    chunks = chunk_pages([page])
    assert any(c['text'] == rows[0] for c in chunks)


def test_extraction_failure_not_missing_price():
    with pytest.raises(IngestionError):
        extract_page('<h1>Adrenal</h1><main class="article-dt-desc"><p>'+'Description. '*30+'</p></main>', SOURCES[2])


def test_missing_expected_container_is_not_accepted():
    with pytest.raises(IngestionError):
        extract_page('<body>Cloudflare challenge</body>', SOURCES[0])


def test_nested_article_paragraph_is_not_duplicated():
    html = '<h1>Profile</h1><main class="article-dt-desc"><p><h2>Section A</h2><p>' + 'A source description. '*20 + '</p><h2>Section B</h2><p>Another complete source paragraph.</p></p></main>'
    page = extract_page(html, SOURCES[0])
    assert len(page['blocks']) == 2
    assert page['blocks'][0]['heading'] == 'Section A'


def test_video_titles_are_ingested_without_following_links():
    html = '<h1>Clinic videos</h1><main class="article-dt-desc"><div class="related-videos-card"><h3><a href="https://example.com/video">Published clinic video title</a></h3></div><p>' + 'Clinic description. '*20 + '</p></main>'
    page = extract_page(html, SOURCES[4])
    assert any(b['text'] == 'Video title: Published clinic video title' for b in page['blocks'])


def test_outside_redirect_is_not_followed(monkeypatch):
    class Response:
        status_code = 302
        headers = {'Location':'https://example.com/extra'}
    crawler = Crawler()
    monkeypatch.setattr(crawler.session, 'get', lambda *a, **k: Response())
    with pytest.raises(IngestionError, match='outside'):
        crawler._get(SOURCES[0].url)
