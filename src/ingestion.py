"""Fetch only the assessment allowlist; fail closed on robots/access/extraction errors."""
import hashlib
import re
import time
from datetime import datetime, timezone
from urllib.parse import urljoin
from urllib.robotparser import RobotFileParser

import requests
from bs4 import BeautifulSoup

from .config import ALLOWED_URLS, REQUEST_INTERVAL, ROBOTS_URL, SOURCES, TIMEOUT, USER_AGENT


class IngestionError(RuntimeError):
    pass


def clean(text):
    return re.sub(r'\s+', ' ', text).strip()


class Crawler:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': USER_AGENT})
        self.last_request = 0.0
        self.robots = None
        self.robots_text = ''
        self.interval = REQUEST_INTERVAL

    def _get(self, url):
        # Redirects are handled explicitly so requests cannot silently leave the allowlist.
        time.sleep(max(0, self.interval - (time.monotonic() - self.last_request)))
        self.last_request = time.monotonic()
        try:
            response = self.session.get(url, timeout=TIMEOUT, allow_redirects=False)
            if response.status_code in (301, 302, 303, 307, 308):
                target = urljoin(url, response.headers.get('Location', ''))
                if target not in ALLOWED_URLS:
                    raise IngestionError('Redirect outside the seven allowed URLs was blocked.')
                if not self.robots or not self.robots.can_fetch(USER_AGENT, target):
                    raise IngestionError('Redirect blocked by robots policy.')
                # Do not follow chains automatically.
                time.sleep(self.interval)
                self.last_request = time.monotonic()
                response = self.session.get(target, timeout=TIMEOUT, allow_redirects=False)
            response.raise_for_status()
            if response.status_code != 200:
                raise IngestionError('The page did not return a usable response.')
            if len(response.content) > 5_000_000:
                raise IngestionError('Page exceeded the extraction size limit.')
            return response
        except requests.RequestException as exc:
            # Never include request headers or provider credentials in errors.
            raise IngestionError('A source could not be fetched; the existing index was retained.') from exc

    def load_robots(self):
        self.robots_text = self._get(ROBOTS_URL).text
        if '<html' in self.robots_text.lower() or 'user-agent:' not in self.robots_text.lower():
            raise IngestionError('robots.txt could not be verified. Refresh stopped.')
        self.robots = RobotFileParser()
        self.robots.parse(self.robots_text.splitlines())
        delay = self.robots.crawl_delay(USER_AGENT)
        rate = self.robots.request_rate(USER_AGENT)
        self.interval = max(REQUEST_INTERVAL, delay or 0, rate.seconds / rate.requests if rate else 0)

    def fetch_all(self, progress=None):
        self.load_robots()
        pages = []
        for source in SOURCES:
            if not self.robots.can_fetch(USER_AGENT, source.url):
                raise IngestionError(f'robots.txt disallows source {source.id}; refresh stopped.')
            response = self._get(source.url)
            if 'text/html' not in response.headers.get('Content-Type', '').lower():
                raise IngestionError(f'Unexpected content type for source {source.id}.')
            pages.append(extract_page(response.text, source))
            if progress:
                progress(len(pages), len(SOURCES))
        return pages


def extract_page(html, source):
    soup = BeautifulSoup(html, 'html.parser')
    title_node = soup.find('h1') or soup.title
    title = clean(title_node.get_text(' ', strip=True)) if title_node else source.id
    # On the comparison page an outer <main> also contains unrelated recommendations.
    # The inner article main is the bounded knowledge content on all seven pages.
    body = soup.select_one('main.article-dt-desc')
    if body is None:
        raise IngestionError(f'Expected content container missing for {source.id}.')
    header = soup.select_one('.pack-title-price-header')
    header_price = header.select_one('.pack-price-block') if header else None
    for node in body.select('script,style,nav,form,footer,button,iframe,noscript,.social-popup-main,.modal'):
        node.decompose()
    blocks = []
    if header_price:
        value = clean(header_price.get_text(' ', strip=True))
        value = re.sub(r'Medical Center Reviews.*?(?=\$)', '', value)
        if re.search(r'\$|USD|EUR|MXN', value):
            blocks.append({'kind': 'paragraph', 'heading': 'Package price', 'text': value})
    heading = title
    seen = set()
    for node in body.find_all(['h1', 'h2', 'h3', 'h4', 'p', 'li', 'table']):
        if node.find_parent('table') or (node.name in ('p', 'li') and node.find_parent('li')):
            continue
        # The site's rich HTML sometimes nests a whole article inside a <p>.
        # Reading that wrapper duplicates every section and breaks heading relevance.
        if node.name == 'p' and node.find(['p', 'h1', 'h2', 'h3', 'h4', 'table', 'ul', 'ol']):
            continue
        if node.name.startswith('h'):
            if source.page_type == 'clinic_videos' and node.name == 'h3' and node.find_parent(class_='related-videos-card'):
                heading = 'Published video titles (titles only; no transcripts fetched)'
                text = 'Video title: ' + clean(node.get_text(' ', strip=True))
                if text not in seen:
                    blocks.append({'kind':'paragraph', 'heading':heading, 'text':text})
                    seen.add(text)
                continue
            heading = clean(node.get_text(' ', strip=True))
            continue
        if node.name == 'table':
            rows = []
            for row in node.find_all('tr'):
                cells = [clean(cell.get_text(' ', strip=True)) for cell in row.find_all(['th', 'td'], recursive=False)]
                if cells:
                    rows.append(cells)
            if not rows:
                continue
            headers = rows[0]
            # Each row carries its own column labels, preserving currency and package context.
            if len(rows) == 1:
                texts = [' | '.join(headers)]
            else:
                texts = [' | '.join(f'{headers[i] if i < len(headers) else "Column"}: {v}' for i, v in enumerate(row)) for row in rows[1:]]
            for text in texts:
                if text not in seen:
                    blocks.append({'kind': 'table_row', 'heading': heading, 'text': text})
                    seen.add(text)
        else:
            text = clean(node.get_text(' ', strip=True))
            if len(text) >= 20 and text not in seen:
                blocks.append({'kind': 'paragraph', 'heading': heading, 'text': text})
                seen.add(text)
    # Some listing cards use divs rather than paragraphs. Preserve their visible text
    # if semantic extraction leaves the allowed page effectively empty.
    if sum(len(b['text']) for b in blocks) < 200:
        text = clean(body.get_text(' ', strip=True))
        if len(text) < 200:
            raise IngestionError(f'Incomplete extraction for source {source.id}.')
        blocks = [{'kind': 'paragraph', 'heading': title, 'text': text}]
    text = '\n'.join(f"{b['heading']}\n{b['text']}" for b in blocks)
    price_count = len(re.findall(r'(?:\$\s*[\d,]+|(?:USD|EUR|MXN)\s*[\d,]+)', text))
    # A missing table on these known price-bearing page types is an extraction problem,
    # never evidence that the website has no listed price.
    if source.page_type in ('treatment_package', 'price_list', 'price_comparison') and not price_count:
        raise IngestionError(f'Price extraction could not be verified for source {source.id}.')
    return {
        'id': source.id, 'url': source.url, 'page_type': source.page_type,
        'title': title, 'text': text, 'blocks': blocks,
        'hash': hashlib.sha256(text.encode()).hexdigest(),
        'fetched_at': datetime.now(timezone.utc).isoformat(),
        'extraction_status': 'verified', 'price_mentions': price_count,
    }
