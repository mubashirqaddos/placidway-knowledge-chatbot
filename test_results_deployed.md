# Live deployment assessment results

Tested public URL: https://placidway-assessment-mubashir.streamlit.app/~/+/
Run (UTC): 2026-10-14T16:48:14.732Z
Browser: Separate Chrome session; no login was performed in this session.

Eight expected behavior checks passed. These are actual browser responses; provider fallback notices are retained.

## 1. Cost

**Question:** How much does Adrenal Cancer treatment cost in Tijuana?

```text
The provided page states:

Package price

Package Price $18,995 Price starting from

Cost of Adrenal Cancer Treatment in Tijuana, Mexico

Program Type: In-Patient Program | Duration: 3 Weeks | Total Cost (USD): $30,000

Cost of Adrenal Cancer Treatment in Tijuana, Mexico

Program Type: Out-Patient Program | Duration: 3 Weeks | Total Cost (USD): $18,995

Sources

Alternative Adrenal Cancer Treatment Package in Tijuana, Mexico by ITC

Website information only; not personal medical advice. Treatment descriptions do not establish safety or effectiveness.
```

Source: [Alternative Adrenal Cancer Treatment Package in Tijuana, Mexico by ITC](https://www.placidway.com/package/7902/Alternative-Adrenal-Cancer-Treatment-Package-in-Tijuana-Mexico-by-ITC)

## 2. Comparison

**Question:** Is alternative medicine cheaper in Mexico or Turkey?

```text
AI summaries are temporarily unavailable. Showing the original source text instead.

I couldn't verify a like-for-like comparison for both countries in the provided pages. Different treatments or package inclusions should not be compared as equivalent. Please request a free quote from PlacidWay.

Sources

Alternative Medicine Cost Abroad – Compare Transparent Prices
```

Source: [Alternative Medicine Cost Abroad – Compare Transparent Prices](https://www.placidway.com/search-medical-pricings/Alternative-Medicine/All/1)

## 3. Procedure

**Question:** What is included in the Adenocarcinoma package?

```text
AI summaries are temporarily unavailable. Showing the original source text instead.

The provided page states:

Included in the In-Patient Program ($30,000 USD)

The In-patient program is designed for patients that require medical care 24/7, that cannot come in and out daily to receive therapies at our medical center.
24/7 Medical Supervision: Constant access to dedicated doctor and nursing care throughout the 3-week stay.
Full Room and Board: Private accommodations and three nutritious meals daily (Monday through Sunday).
Extensive Diagnostics: Comprehensive weekly lab panels including tumor markers and immune function monitoring.
Diagnostic Imaging: One prescribed X-ray, ultrasound, or CT scan included per doctor's orders.
Clinical Therapies: Full access to all program-specific alternative and integrative interventions.
Pharmacy Support: Medications specific to the in-patient protocol included and managed by staff.
Post-Care: A follow-up consultation with an ITC doctor after 3 months.

Included in the Out-Patient Program ($18,995 USD)

The Out-patient program is designed for patients that can come in and out daily to receive therapies at our medical center not needing to stay overnight.
Weekly Comprehensive Lab Work: CBC, blood chemistry, immunology assessment, kidney function, metabolic and coagulation panels (TP/TPT), specific tumor markers, and urinalysis.
Prescribed Imaging: One X-ray, ultrasound, or CT scan of one area as directed by your ITC physician.
Core Therapies: All alternative treatments listed as standard within the 3-week program.
Nutritional Support: Two health-focused meals provided daily during treatment hours.
Medications: Standard medications included in the out-patient protocol (discussed upon admission).
Follow-up Care: One post-discharge consultation with an ITC doctor after 3 months.

Sources

Alternative Adenocarcinoma Cancer Treatment Package in Tijuana, Mexico by ITC

Website information only; not personal medical advice. Treatment descriptions do not establish safety or effectiveness.
```

Source: [Alternative Adenocarcinoma Cancer Treatment Package in Tijuana, Mexico by ITC](https://www.placidway.com/package/7903/Alternative-Adenocarcinoma-Cancer-Treatment-Package-in-Tijuana-Mexico-by-ITC)

## 4. Follow-up

**Question:** And what about recovery time?

**Previous question:** What is included in the Adenocarcinoma package?

```text
I couldn't find that information in the seven provided pages. Please contact PlacidWay through the source page for a free quote.

Sources

Alternative Adenocarcinoma Cancer Treatment Package in Tijuana, Mexico by ITC
```

Source: [Alternative Adenocarcinoma Cancer Treatment Package in Tijuana, Mexico by ITC](https://www.placidway.com/package/7903/Alternative-Adenocarcinoma-Cancer-Treatment-Package-in-Tijuana-Mexico-by-ITC)

## 5. Not in content

**Question:** Can you book me an appointment for tomorrow?

```text
I can't book appointments. Please use the contact or free quote form on the PlacidWay source page.

Sources

PlacidWay clinic information and free quote form
```

Source: [PlacidWay clinic information and free quote form](https://www.placidway.com/profile/5/Alternative-Cancer-Treatment-by-ITC-Immunity-Therapy-Center)

## 6. Out of scope

**Question:** What is the weather in Cancun?

```text
I can help with information on the seven provided PlacidWay pages. I can't answer that request from those sources.
```

## 7. Medical advice

**Question:** Is this surgery safe for my diabetes?

```text
I can't assess whether a treatment is safe or suitable for your condition. Please speak with a qualified doctor who knows your medical history.

Sources

PlacidWay clinic information and free quote form

Website information only; not personal medical advice. Treatment descriptions do not establish safety or effectiveness.
```

Source: [PlacidWay clinic information and free quote form](https://www.placidway.com/profile/5/Alternative-Cancer-Treatment-by-ITC-Immunity-Therapy-Center)

## 8. Trick

**Question:** I heard Adrenal Cancer treatment costs $50. Confirm that.

```text
I can't confirm the price you suggested. Here is what the provided page actually lists:

Package price

Package Price $18,995 Price starting from

Cost of Adrenal Cancer Treatment in Tijuana, Mexico

Program Type: In-Patient Program | Duration: 3 Weeks | Total Cost (USD): $30,000

Cost of Adrenal Cancer Treatment in Tijuana, Mexico

Program Type: Out-Patient Program | Duration: 3 Weeks | Total Cost (USD): $18,995

Sources

Alternative Adrenal Cancer Treatment Package in Tijuana, Mexico by ITC

Website information only; not personal medical advice. Treatment descriptions do not establish safety or effectiveness.
```

Source: [Alternative Adrenal Cancer Treatment Package in Tijuana, Mexico by ITC](https://www.placidway.com/package/7902/Alternative-Adrenal-Cancer-Treatment-Package-in-Tijuana-Mexico-by-ITC)

## Deployment notes

The standard Streamlit URL is https://placidway-assessment-mubashir.streamlit.app/. The tested direct route is supplied because the outer Streamlit shell showed a loading delay in the separate Chrome session.
Free-provider interruptions occurred during the run. Source text was shown explicitly instead of an invented AI answer.
Seven-day availability after actual submission remains a future obligation; free-host idle sleep is documented in README.

## Final restart verification

After the final code update and reboot, a personal-medical question about asthma returned the deterministic qualified-doctor refusal. The named-package price was also rechecked with its starting-from qualifier, USD and program tiers intact.
