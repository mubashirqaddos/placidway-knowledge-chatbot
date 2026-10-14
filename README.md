# PlacidWay Website Knowledge Chatbot

[Open the public chatbot](https://placidway-assessment-mubashir.streamlit.app/~/+/) · [Standard Streamlit URL](https://placidway-assessment-mubashir.streamlit.app/)

A small, source-grounded chatbot for the **AI Automation Assessment: Website Knowledge Chatbot**. Its knowledge is restricted to the seven URLs supplied in the assessment. It answers published package/clinic/cost questions, cites the actual source pages, declines personal medical advice and unsupported requests, and offers a free-quote contact path.

## Stack and reasons

- **Python 3.12 + Streamlit:** a simple chat interface and free Community Cloud deployment.
- **Requests + Beautiful Soup:** explicit robots policy, identifiable User-Agent, sequential rate-limited fetches and targeted HTML extraction. No autonomous link crawling.
- **BM25 + FastEmbed (`BAAI/bge-small-en-v1.5`):** complementary keyword and semantic search. Embeddings run locally on CPU through ONNX; no embedding API bill, vector database or GPU is required.
- **NumPy + JSON:** 167 chunks in the initial verified snapshot; straightforward inspection and atomic replacement. No pickle or committed database binaries.
- **Gemini `gemini-3.1-flash-lite`:** configurable JSON-schema generation on a model with an advertised free API tier when checked on 14 October 2026. A project must remain on the **Free tier**; this app cannot determine or change the account's billing tier. No paid model fallback or external search is used. Check availability/quota in your own Google AI Studio account before deployment.

## Architecture

```text
7 exact allowed URLs + robots.txt
  -> ingestion (User-Agent, >=1.05 s between requests, timeout, redirect guard)
  -> raw extracted JSON, heading-aware chunks, intact labelled table rows
  -> local vectors + JSON snapshot (atomic index replacement)

question -> policy routing -> follow-up resolution / bounded English search rewrite
         -> BM25 + vector retrieval -> RRF ordering + relevance gate -> top 5
         -> Gemini structured claims -> evidence/number/source validation
         -> answer + source links constructed in code
```

The crawler does not follow page links, video links, related clinics, forms, pagination, JavaScript endpoints or sitemaps. It fetches robots.txt solely to check access. Redirects outside the seven exact allowed URLs are blocked. All seven pages had readable server-rendered content during the initial run; no browser scraper or API-endpoint fallback was needed.

### Grounding and fallbacks

- User-suggested prices are never accepted as evidence.
- Each generated factual claim needs an exact continuous evidence quote and a retrieved chunk ID. Unknown chunk IDs, outside source URLs, unsupported numbers and generated links are rejected.
- Named-package cost responses use original source rows directly without an LLM call. Other cost responses also render original evidence, including its section heading, currency, program type and duration, rather than relying on a model's price paraphrase.
- A missing or failed extraction stops refresh; it never becomes a claim that a price is absent.
- Provider errors: the bot explicitly labels a source-excerpt fallback when source evidence is available. A rejected model output also falls back to conservative source excerpts.
- No relevant evidence: a deterministic localized fallback suggests contacting PlacidWay for a free quote. No LLM call is spent writing a refusal.
- Personal medical advice and appointment booking are routed to fixed responses. A treatment's three-week program is not presented as recovery time. Clinical advertising is not evidence of efficacy.
- `RRF` is used for ranking, not as a confidence probability. Thresholds are configurable and heuristic, not a guarantee of correctness.
- An empty Gemini key enables an explicitly labelled **source excerpt mode**, which quotes relevant source text and conservatively declines comparisons. It is useful for local inspection; it is not evidence that Gemini integration has been tested.

## Local setup

```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS / Linux:
# source .venv/bin/activate
python -m pip install -r requirements.txt
```

Copy `.streamlit/secrets.example.toml` to `.streamlit/secrets.toml` and fill in values locally. Never commit this file. OS environment variables are also supported; local Streamlit secrets take precedence in the app. `.env.example` is a reference, not an automatically loaded dotenv file.

```toml
GEMINI_API_KEY = "your-free-tier-key"
GEMINI_MODEL = "gemini-3.1-flash-lite"
ADMIN_TOKEN = "a-long-random-admin-secret"
CONTACT_EMAIL = ""
```

`CONTACT_EMAIL` is optional and must be a verified recipient if configured. No assumed hiring email or invented clinic contact address is included. The clinic page itself contains the quote/contact form. The app never posts to that form or sends email automatically.

The checked-in knowledge snapshot lets the app start without fetching medical pages again. To update content:

```bash
python ingest.py
```

The first semantic-index build/query can take longer while the free model downloads. Subsequent runs use a local cache. `python ingest.py --bm25-only` creates a lexical-only snapshot if local model resources are unavailable. For normal hybrid operation, omit that flag.

```bash
streamlit run app.py
```

Open the localhost URL printed by Streamlit. Example buttons, message history, verified source links, last successful refresh, and a password-protected admin refresh are in the interface. An invalid or missing admin token cannot refresh. If no snapshot exists, startup attempts the same bounded seven-page build; errors show a friendly message.

## Refresh and data

`src/config.py` contains the allowlist, `TOP_K`, chunk size, relevance thresholds, history limit and model defaults. A process/file lock prevents concurrent refreshes. A complete new snapshot is validated before `os.replace` makes it active; a failed fetch or model build leaves the previous index in service. `data/raw/` contains extracted source JSON with URL, title, type, text, SHA-256 hash and UTC timestamp; `data/index.json` carries aligned chunks, vectors and source metadata. Raw files are audit records; the app reads only the atomic snapshot. A crashed process may leave `data/refresh.lock`; verify that no refresh process is running before manually removing that lock.

Unanswered-question logs are local JSONL with email/phone redaction and bounded rotation. They are excluded from Git and may disappear on cloud restart. Do not enter private medical details into this demo. Google's free API tier has different data-use terms from paid services; see the official pricing/terms links below.

The optional quote form prepares a name/email draft in the current session. It explicitly states that nothing was sent, supports a local download, and links to the original PlacidWay page for submission. No lead is silently transmitted, committed or written into the question log.

## Tests and actual assessment answers

```bash
python -m pip install -r requirements-dev.txt
python -m pytest -q
python run_eval.py --mode extractive
python run_eval.py --mode gemini
```

`test_results.md/json` record actual excerpt-mode outputs. `test_results_gemini.md/json`, when present, record the actual configured Gemini run. They include the eight supplied question categories, with the exact disease and destination filled from the allowed pages. Q4 explicitly follows the adenocarcinoma-package question. The wrong-price question specifies the package so it cannot accidentally retrieve an unrelated consultation fee.

Tests cover source/ID validation, invented numbers and evidence, prompt injection, table/currency extraction, outside redirects, personal advice, country follow-ups, unsupported treatments, recovery-time confusion, and Streamlit chat rendering. Unit/UI tests use no paid service and avoid API calls. See `verification.md` for the latest executed checks and remaining external deployment tasks.

## Free deployment: Streamlit Community Cloud

1. Push this folder's contents to a GitHub repository. Include `data/index.json` and `data/raw/`. Exclude secrets, `.cache`, logs and local virtual environments; `.gitignore` is supplied.
2. Sign in to [Streamlit Community Cloud](https://share.streamlit.io/) with the intended GitHub account, select the repository/branch and `app.py`, and choose Python 3.12. Dependencies come from `requirements.txt`.
3. Paste owner secrets in **Advanced settings / Secrets**. Use a free-tier Google project. Do not expose keys through a sidebar or repository. New GitHub/Streamlit permission grants or account terms must be reviewed by the owner.
4. Deploy with public viewer access and record the **actual returned URL** in `submission.md`. Test it in a signed-out/incognito session using all eight questions; a localhost test is not a public deployment test.
5. Keep the app available for at least seven days after submission. **Community Cloud hibernates after 12 hours without traffic** and visitors can wake it. Once-daily visits do not guarantee continuous availability. Do not claim strict uninterrupted uptime; resolve this assessment requirement with the reviewer if sleep is unacceptable. Do not enable paid hosting without the owner's explicit change to the free-only requirement.

The app was deployed on 14 October 2026, with public viewer access and a private source repository. The direct public app route above was verified in a separate Chrome session; it avoids an outer Streamlit loading-screen delay observed during verification. See `test_results_deployed.md` for the live browser run when present. The standard Streamlit URL remains available as well.

## Project structure

```text
app.py                     Streamlit chat UI
ingest.py                  CLI refresh
run_eval.py                Actual eight-question reports
src/config.py              Scope and tuning constants
src/ingestion.py            Robots, allowlist, HTML/table extraction
src/chunking.py             Heading-aware chunks
src/retrieval.py            BM25, local embeddings, RRF, destination checks
src/knowledge.py            Snapshot storage and refresh
src/llm.py                  Gemini client, bounded retries, JSON schema
src/prompts.py              Bounded generation instructions
src/guardrails.py           Routing, localized fallbacks, evidence checks
src/answering.py            Question pipeline and source construction
src/logging_hooks.py        Local content-gap logging
data/raw/                  Seven extracted source records and robots policy
data/index.json             Portable hybrid knowledge snapshot
tests/                     Unit, source and UI verification
README.md                  Setup, architecture, refresh, deployment
limitations.md             Half-page improvement/limitations write-up
test_results*.md/json      Actual assessment answers, labelled by mode
verification.md            Check results and deployment status
submission.md              Submission checklist; unknown recipients stay pending
```

## Official references

- [Gemini free-tier pricing and data-use notes](https://ai.google.dev/gemini-api/docs/pricing)
- [Gemini model documentation](https://ai.google.dev/gemini-api/docs/models/gemini-3.1-flash-lite)
- [Structured outputs](https://ai.google.dev/gemini-api/docs/structured-output)
- [Streamlit secrets](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/secrets-management)
- [Streamlit app hibernation](https://docs.streamlit.io/deploy/streamlit-community-cloud/manage-your-app)
- [FastEmbed model documentation](https://qdrant.github.io/fastembed/examples/Supported_Models/)
