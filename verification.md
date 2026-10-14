# Verification record

Verified locally on 14 October 2026. This record distinguishes local checks from public deployment checks.

## Executed

- The exact seven URLs from the assessment's PDF hyperlinks were fetched successfully with an identifiable User-Agent and robots checks. No linked page, video transcript, sitemap or extra endpoint was crawled.
- Rebuilt the index after fixing an invalid nested-paragraph wrapper in the site's HTML. The active snapshot contains **167 heading-aware chunks** and aligned local vectors from **seven sources**. Video titles are included as titles only.
- Confirmed the package price tables retain USD, inpatient/outpatient labels and the three-week program duration. No recovery time is inferred from program duration.
- `python -m pytest -q`: **28 passed**. This includes unit, source-extraction and Streamlit AppTest checks.
- `python run_eval.py --mode extractive`: actual answers saved in `test_results.md/json`.
- `python run_eval.py --mode gemini`: actual configured free-tier integration run saved in `test_results_gemini.md/json`. Named-package prices use source rows; personal advice, booking and out-of-scope questions use policy responses; the package-inclusion and recovery questions exercised Gemini. The comparison used an explicitly labelled excerpt fallback after a temporary provider failure. It did not make an unsupported country ranking.
- Local browser: a real cost question displayed source-linked USD program prices. Additional browser verification and screenshots are retained with the deliverable.
- Gemini returned temporary HTTP 503 errors during testing. Provider failures are handled without raw tracebacks or invented answers; available source evidence is shown with an explicit fallback notice.

## External state

- Source repository created: `https://github.com/mubashirqaddos/placidway-knowledge-chatbot` (private).
- Code push: pending confirmation.
- Public deployment and signed-out eight-question run: pending.
- Seven-day availability period: not started until a real public deployment exists.
- No assessment email was sent. The actual hiring recipient and reviewer username are not available in the supplied PDF.

## Scope

This is a website knowledge chatbot, not a booking system or medical decision tool. The source allowlist, grounded answers, honest fallback, price context, chat UI and refresh are implemented. A public URL remains a required assessment deliverable until deployment is verified.
