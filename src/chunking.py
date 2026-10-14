"""Heading-aware chunks with complete, labelled price-table rows."""
import hashlib
import re
from .config import CHUNK_WORDS


def chunk_pages(pages):
    chunks = []
    for page in pages:
        parts, current, heading = [], [], ''

        def flush():
            nonlocal current
            if current:
                parts.append((heading, '\n'.join(current)))
                current = []

        for block in page['blocks']:
            if block['heading'] != heading:
                flush()
                heading = block['heading']
            text = block['text']
            if block['kind'] == 'table_row':
                flush()
                parts.append((heading, text))
                continue
            # Split large prose by sentences; never split a labelled table row.
            sentences = re.split(r'(?<=[.!?])\s+', text) if len(text.split()) > CHUNK_WORDS else [text]
            for sentence in sentences:
                if current and len((' '.join(current) + sentence).split()) > CHUNK_WORDS:
                    flush()
                current.append(sentence)
        flush()
        for i, (section, text) in enumerate(parts):
            full = f"{page['title']}\n{section}\n{text}"
            chunks.append({
                'id': f"{page['id']}-{i}-{hashlib.sha256(full.encode()).hexdigest()[:8]}",
                'page_id': page['id'], 'url': page['url'], 'title': page['title'],
                'page_type': page['page_type'], 'heading': section, 'text': text,
                'search_text': full, 'fetched_at': page['fetched_at'],
            })
    return chunks
