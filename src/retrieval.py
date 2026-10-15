"""Small-file BM25 + local ONNX embeddings, merged using reciprocal rank fusion."""
import math
import re
from collections import Counter
from functools import lru_cache

import numpy as np

from .config import EMBEDDING_MODEL, MIN_LEXICAL_COVERAGE, MIN_VECTOR_SIMILARITY, ROOT, TOP_K

STOP = set('a an the is are was were be been it its this that these those i me my you your we our they their to of in on at for from and or with by as how what which where when can could would should does do did please tell about much more heard confirm'.split())
ALIASES = {'costs':'price','cost':'price','prices':'price','pricing':'price','included':'include','includes':'include','inclusions':'include','cheaper':'compare','cheapest':'compare','comparing':'compare','comparison':'compare','recovery':'recovery','recover':'recovery'}
CONDITIONS = ('adenocarcinoma', 'adrenal', 'anal')
DESTINATIONS = ('mexico','turkey','thailand','croatia','india','canada','germany','spain','georgia','brazil','china','japan','korea','jamaica','saudi arabia','united states','united kingdom')


def tokenize(text):
    words = re.findall(r'[a-z0-9]+', text.lower())
    return [ALIASES.get(w, w) for w in words if w not in STOP and not w.isdigit()]


@lru_cache(maxsize=1)
def embedding_model():
    from fastembed import TextEmbedding
    return TextEmbedding(model_name=EMBEDDING_MODEL, cache_dir=str(ROOT / '.cache' / 'embeddings'), threads=2)


def embed_documents(chunks):
    vectors = np.asarray(list(embedding_model().embed([c['search_text'] for c in chunks], batch_size=16)), dtype=np.float32)
    norms = np.linalg.norm(vectors, axis=1, keepdims=True)
    return (vectors / np.maximum(norms, 1e-9)).tolist()


class Retriever:
    def __init__(self, snapshot, use_vectors=True):
        self.snapshot = snapshot
        self.chunks = snapshot['chunks']
        self.docs = [Counter(tokenize(c['search_text'])) for c in self.chunks]
        self.lengths = [sum(d.values()) for d in self.docs]
        self.avg_length = sum(self.lengths) / max(1, len(self.docs))
        frequency = Counter(t for doc in self.docs for t in doc)
        n = len(self.docs)
        self.idf = {t: math.log(1 + (n - df + .5) / (df + .5)) for t, df in frequency.items()}
        self.vectors = np.asarray(snapshot.get('vectors', []), dtype=np.float32)
        self.use_vectors = use_vectors and len(self.vectors) == len(self.chunks)

    def retrieve(self, question, top_k=TOP_K):
        tokens = set(tokenize(question))
        if not tokens:
            return []
        condition = next((c for c in CONDITIONS if re.search(r'\b' + c + r'\b', question, re.I)), None)
        candidates = [i for i, c in enumerate(self.chunks) if not condition or c['page_id'] == condition]
        countries = [c for c in DESTINATIONS if re.search(r'\b' + c + r'\b', question, re.I)]
        if countries:
            # A destination follow-up must not reuse a package from a different country.
            # For a named package its title supplies the location, not incidental prose.
            candidates = [i for i in candidates if any(country in (self.chunks[i]['title'] if condition else self.chunks[i]['search_text']).lower() for country in countries)]
        if condition:
            # Do not silently reuse Mexico for an unsupported place such as Pakistan
            # merely because the place is absent from our common-country vocabulary.
            places = re.findall(r'\bin\s+([a-z][a-z ]{1,35}?)(?=\s+(?:for|with|and|or|cost|price|treatment|package|please)\b|[?.,!\[\]]|$)', question.lower())
            for place in places:
                place = place.strip()
                if not place.startswith(('the ', 'a ', 'an ')):
                    candidates = [i for i in candidates if place in self.chunks[i]['title'].lower()]
        if condition and 'include' in tokens:
            # Package-wide wording occurs throughout a page. Inclusions need the
            # actual labelled program sections, not a paragraph about cost.
            candidates = [i for i in candidates if re.search(r'\b(included|includes|inclusions)\b', self.chunks[i]['heading'], re.I)]
        if not condition and len(countries) > 1 and 'compare' in tokens:
            # Cross-country pricing comes from the supplied comparison page,
            # rather than the last disease package discussed in the chat.
            candidates = [i for i in candidates if self.chunks[i]['page_id'] == 'comparison']
        if not candidates:
            return []
        scores, coverage = {}, {}
        for i in candidates:
            doc = self.docs[i]
            scores[i] = sum(self.idf.get(t, 0) * doc[t] * 2.5 / (doc[t] + 1.5 * (.25 + .75 * self.lengths[i] / max(self.avg_length, 1))) for t in tokens if doc[t])
            coverage[i] = len(tokens & set(doc)) / len(tokens)
        lexical = sorted(candidates, key=lambda i: scores[i], reverse=True)
        semantic, cosines = [], {}
        if self.use_vectors:
            query = np.asarray(next(iter(embedding_model().query_embed(question))), dtype=np.float32)
            query /= max(float(np.linalg.norm(query)), 1e-9)
            similarities = self.vectors @ query
            cosines = {i: float(similarities[i]) for i in candidates}
            semantic = sorted(candidates, key=lambda i: cosines[i], reverse=True)
        rrf = Counter()
        for order in (lexical[:20], semantic[:20]):
            for rank, i in enumerate(order, 1):
                rrf[i] += 1 / (60 + rank)
        results = []
        for i in sorted(rrf, key=rrf.get, reverse=True):
            # RRF orders candidates. It is not a confidence score.
            if coverage[i] < MIN_LEXICAL_COVERAGE and cosines.get(i, 0) < MIN_VECTOR_SIMILARITY:
                continue
            results.append({**self.chunks[i], 'lexical_coverage': coverage[i], 'cosine': cosines.get(i), 'rrf': rrf[i]})
            if len(results) == top_k:
                break
        return results
