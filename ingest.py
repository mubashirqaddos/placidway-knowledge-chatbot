"""Refresh only the seven assessment pages. No web crawling beyond the allowlist."""
import argparse
from src.knowledge import refresh

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--bm25-only', action='store_true', help='Skip local vector generation; BM25 still works.')
    args = parser.parse_args()
    try:
        snapshot = refresh(lambda done,total: print(f'Fetched {done}/{total} allowed pages', flush=True), not args.bm25_only)
        print(f"Saved {len(snapshot['chunks'])} chunks from {len(snapshot['pages'])} sources. Vectors: {bool(snapshot['vectors'])}")
    except Exception as exc:
        # CLI is for the owner; no credentials are placed in exception messages.
        print(f'Refresh stopped: {exc}')
        raise SystemExit(1)
