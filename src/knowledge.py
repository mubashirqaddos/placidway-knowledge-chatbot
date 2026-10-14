"""One atomic snapshot ties chunks, vectors and source metadata together."""
import json
import os
import tempfile
import threading
from datetime import datetime, timezone

from .chunking import chunk_pages
from .config import ALLOWED_URLS, DATA, EMBEDDING_MODEL, INDEX, SOURCES
from .ingestion import Crawler, IngestionError
from .retrieval import embed_documents

_refresh_lock = threading.Lock()


def load_index(path=INDEX):
    value = json.loads(path.read_text(encoding='utf-8'))
    if value.get('schema_version') != 1 or not value.get('chunks'):
        raise ValueError('Unsupported or empty knowledge snapshot.')
    if {p['url'] for p in value['pages']} != ALLOWED_URLS:
        raise ValueError('The index must contain exactly the seven allowed sources.')
    ids = set()
    for chunk in value['chunks']:
        if chunk['url'] not in ALLOWED_URLS or chunk['id'] in ids:
            raise ValueError('Invalid knowledge provenance.')
        ids.add(chunk['id'])
    vectors = value.get('vectors', [])
    if vectors and len(vectors) != len(value['chunks']):
        raise ValueError('Vector and chunk counts do not match.')
    return value


def refresh(progress=None, with_vectors=True):
    DATA.mkdir(parents=True, exist_ok=True)
    if not _refresh_lock.acquire(blocking=False):
        raise IngestionError('Another refresh is already in progress.')
    lock = DATA / 'refresh.lock'
    acquired_file = False
    temp_path = None
    try:
        try:
            fd = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            acquired_file = True
            os.close(fd)
        except FileExistsError as exc:
            raise IngestionError('Another refresh is in progress. If a process crashed, remove data/refresh.lock after checking it has stopped.') from exc
        crawler = Crawler()
        pages = crawler.fetch_all(progress)
        chunks = chunk_pages(pages)
        vectors = embed_documents(chunks) if with_vectors else []
        snapshot = {
            'schema_version': 1, 'refreshed_at': datetime.now(timezone.utc).isoformat(),
            'embedding_model': EMBEDDING_MODEL if vectors else None,
            'pages': [{k:v for k,v in p.items() if k not in ('blocks', 'text')} for p in pages],
            'chunks': chunks, 'vectors': vectors,
            'robots_checked_at': datetime.now(timezone.utc).isoformat(),
        }
        with tempfile.NamedTemporaryFile('w', encoding='utf-8', dir=DATA, prefix='index.', suffix='.tmp', delete=False) as f:
            temp_path = f.name
            json.dump(snapshot, f, ensure_ascii=False, separators=(',', ':'))
        load_index(__import__('pathlib').Path(temp_path))
        raw = DATA / 'raw'
        raw.mkdir(exist_ok=True)
        for page in pages:
            (raw / f"{page['id']}.json").write_text(json.dumps(page, ensure_ascii=False, indent=2), encoding='utf-8')
        (raw / 'robots.txt').write_text(crawler.robots_text, encoding='utf-8')
        os.replace(temp_path, INDEX)
        temp_path = None
        return snapshot
    finally:
        if temp_path and os.path.exists(temp_path):
            os.unlink(temp_path)
        if acquired_file:
            lock.unlink(missing_ok=True)
        _refresh_lock.release()
