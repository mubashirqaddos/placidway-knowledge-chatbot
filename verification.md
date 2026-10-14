# Verification record

Verified locally on 14 October 2026. This record distinguishes local checks from public deployment checks.

## Executed

- The exact seven URLs from the assessment's PDF hyperlinks were fetched successfully with an identifiable User-Agent and robots checks. No linked page, video transcript, sitemap or extra endpoint was crawled.
- Rebuilt the index after fixing an invalid nested-paragraph wrapper in the site's HTML. The active snapshot contains **167 heading-aware chunks** and aligned local vectors from **seven sources**. Video titles are included as titles only.
- Confirmed the package price tables retain USD, inpatient/outpatient labels and the three-week program duration. No recovery time is inferred from program duration.
- `python -m pytest -q`: **34 passed**. This includes unit, source-extraction and Streamlit AppTest checks.
- `python run_eval.py --mode extractive`: actual answers saved in `test_results.md/json`.
- `python run_eval.py --mode gemini`: actual configured free-tier integration run saved in `test_results_gemini.md/json`. Named-package prices use source rows; personal advice, booking and out-of-scope questions use policy responses; the package-inclusion and recovery questions exercised Gemini. The comparison cited the two actual Ozone Therapy country rows; it did not invent matched package inclusions or a country-wide ranking. Earlier runs also exercised the labelled provider-error excerpt fallback.
- Downloaded the initial 42-file GitHub archive and compared every file byte-for-byte with the local project: no missing, different or extra files; no API key/admin token in the archive. Later targeted reliability changes add stricter personal-medical routing, shorter provider waits and corresponding tests; the full unit/UI suite then passed 34 tests. The deployed process was rebooted after these source changes. After reboot, the new personal-medical policy returned the clinic-profile contact source before retrieval, and the source-linked USD price tiers and starting-from qualifier were rechecked successfully.
- Local browser: a real cost question displayed source-linked USD program prices. Additional browser verification and screenshots are retained with the deliverable.
- Gemini returned temporary HTTP 503 errors during testing. Provider failures are handled without raw tracebacks or invented answers; available source evidence is shown with an explicit fallback notice.

## Reliability follow-up after screenshot review

- Found and fixed an optional query-rewrite failure that returned `unavailable` before retrieval when a conversation already had history. Provider rewrite failures now retain the original/local history-resolved question and continue source retrieval. This does not repair an upstream Gemini outage or guarantee a generated summary.
- Re-ran the automated suite: **36 passed**. Two regression checks cover comparison retrieval and a package-price follow-up during an HTTP 503 rewrite outage.
- A fresh minimal structured-JSON request using the configured local key and model succeeded. The key/model configuration can work; this single success does not establish sustained provider reliability or diagnose the exact upstream status of each screenshot.
- The earlier eight-question browser record includes safe fallback outputs. It must not be interpreted as proof that AI summaries and matched comparisons are consistently available. Raw package excerpts preserve evidence but do not satisfy the procedure-summary expectation as well as a working grounded summary.
- Core ingestion, sources, cost context, chat, unknown/medical/booking handling and refresh are implemented. Seven-day availability after actual submission remains a future obligation. Free-host sleep and provider interruptions remain material limitations.

## External state

- Source repository created: `https://github.com/mubashirqaddos/placidway-knowledge-chatbot` (private).
- Code uploaded through the signed-in GitHub browser after command-line authentication was unavailable; repository remains private. Source-module and knowledge-snapshot commits were verified in the repository UI.
- Public deployment: https://placidway-assessment-mubashir.streamlit.app/ (public viewer access enabled; source repository stays private). The direct app route /~/+/ opened in a separate Chrome session without a login prompt. The outer Streamlit shell showed a loading delay in that session, so the direct route is supplied as the primary tested link. All eight live assessment questions were run in the separate Chrome session. The actual responses, including provider fallback notices, are saved in test_results_deployed.md/json; all eight behavior checks passed.
- Seven-day availability: deployment verified on 14 October 2026. Keep it available at least seven days after actual submission; this future period is not yet fulfilled and idle hibernation remains a free-host limitation.
- No assessment email was sent. The actual hiring recipient and reviewer username are not available in the supplied PDF.

## Scope

This is a website knowledge chatbot, not a booking system or medical decision tool. The source allowlist, grounded answers, honest fallback, price context, chat UI and refresh are implemented. The required public URL is deployed. The remaining future obligation is availability after actual submission.
