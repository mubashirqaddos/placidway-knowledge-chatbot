from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'data'
INDEX = DATA / 'index.json'
USER_AGENT = 'PlacidWayAssessmentBot/1.0 (seven-page assessment; no link crawling)'
ROBOTS_URL = 'https://www.placidway.com/robots.txt'
REQUEST_INTERVAL = 1.05
TIMEOUT = (10, 35)
TOP_K = 5
CHUNK_WORDS = 220  # Approximately 300-400 English tokens; tables are never split across rows.
MIN_LEXICAL_COVERAGE = 0.22
MIN_VECTOR_SIMILARITY = 0.60
HISTORY_TURNS = 6
EMBEDDING_MODEL = 'BAAI/bge-small-en-v1.5'
GEMINI_MODEL = 'gemini-3.1-flash-lite'
MAX_QUESTION_CHARS = 2000

@dataclass(frozen=True)
class Source:
    id: str
    page_type: str
    url: str

SOURCES = (
    Source('clinic', 'clinic_profile', 'https://www.placidway.com/profile/5/Alternative-Cancer-Treatment-by-ITC-Immunity-Therapy-Center'),
    Source('adenocarcinoma', 'treatment_package', 'https://www.placidway.com/package/7903/Alternative-Adenocarcinoma-Cancer-Treatment-Package-in-Tijuana-Mexico-by-ITC'),
    Source('adrenal', 'treatment_package', 'https://www.placidway.com/package/7902/Alternative-Adrenal-Cancer-Treatment-Package-in-Tijuana-Mexico-by-ITC'),
    Source('anal', 'treatment_package', 'https://www.placidway.com/package/7901/Alternative-Anal-Cancer-Treatment-Package-in-Tijuana-Mexico-by-ITC'),
    Source('videos', 'clinic_videos', 'https://www.placidway.com/profile-videos/5/Alternative-Cancer-Treatment-by-ITC-Immunity-Therapy-Center'),
    Source('prices', 'price_list', 'https://www.placidway.com/price-list/5/Alternative-Cancer-Treatment-by-ITC-Immunity-Therapy-Center'),
    Source('comparison', 'price_comparison', 'https://www.placidway.com/search-medical-pricings/Alternative-Medicine/All/1'),
)
ALLOWED_URLS = frozenset(s.url for s in SOURCES)
