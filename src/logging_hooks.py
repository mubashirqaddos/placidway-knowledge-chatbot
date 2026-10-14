"""Local, redacted content-gap log. Never send questions to an external webhook."""
import json
import re
from datetime import datetime, timezone
from .config import DATA


def log_unanswered(question, answer):
    if answer.status not in ('not_found', 'unavailable'):
        return
    redacted = re.sub(r'[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}', '[email]', question)
    redacted = re.sub(r'\+?\d[\d\s().-]{7,}\d', '[phone/number]', redacted)
    directory = DATA / 'logs'
    try:
        directory.mkdir(parents=True, exist_ok=True)
        # Bound disk use on a free host; no names/emails from the quote form are logged.
        path = directory / 'unanswered.jsonl'
        if path.exists() and path.stat().st_size > 1_000_000:
            path.replace(directory / 'unanswered.previous.jsonl')
        with path.open('a', encoding='utf-8') as f:
            f.write(json.dumps({'at':datetime.now(timezone.utc).isoformat(), 'question':redacted[:500], 'status':answer.status}, ensure_ascii=False) + '\n')
    except OSError:
        pass  # A logging failure must never break the patient's chat.
