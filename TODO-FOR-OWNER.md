# TODO FOR OWNER — Pre-Launch Checklist

Review and confirm each item below in `data/site.json`, `data/research.json`, and templates before publishing to production.

- [ ] **1. Official Domain Email (`data/site.json` -> `entity.email`)**
  - Currently set to `"info@harionresearch.co.in"` (replacing the old `REPLACE_WITH_YOUR_EMAIL` placeholder and the legacy `info@harionresearch.com` address). Confirm that mailbox routing/MX records are active on `harionresearch.co.in`.

- [ ] **2. Grievance Redressal Officer (`data/site.json` -> `grievance_officer`)**
  - The old site listed **Abhilash Bhoyar** in the Privacy Policy and **Shruti Paswan** in the Terms of Service.
  - We unified this to a single officer (`Abhilash Bhoyar`, `info@harionresearch.co.in`) across `/contact/`, `/privacy-policy/`, `/terms/`, and `/refund-policy/`. Confirm the designated officer's name and direct email.

- [ ] **3. Flagship Program Price, Duration & Format (`data/site.json` -> `program`)**
  - Currently populated from the existing site as:
    - `name`: `"Equity Research Internship Program"`
    - `duration`: `"60 days"`
    - `price`: `"₹500 (Certificate fee; 40 classroom lessons free)"`
    - `format`: `"40 self-paced modules + weekly live mentor review session"`
    - `certificate`: `"Verified completion certificate upon report review"`
  - Confirm the exact fee and duration you want displayed across the Homepage, `/equity-research-internship/`, Footer, and Policies, and update the JSON-LD `Course` offer price in `build.py` if the numeric fee changes.

- [ ] **4. PhonePe Payment Gateway Alignment**
  - Verify that the entity name (`Harion Research`), Udyam registration (`UDYAM-MP-22-0035155`), domain (`harionresearch.co.in`), and checkout line item (`Harion Equity Research Internship Program: online training, 60 days`) match your approved PhonePe merchant profile.
  - When ready to switch the Internship **Enroll** button from the Google Form (`https://forms.gle/uPVBmUGSE6gzcrkb8`) to `api.harionresearch.co.in/pay`, update `program.enroll_url` in `data/site.json` (all enroll buttons carry `data-enroll="equity-research-internship"`).

- [ ] **5. Fundamental Filters & Data Source (`data/site.json` -> `screener`)**
  - `screener.fundamental_filters` is currently populated with 10 standard fundamental and structure study metrics (`P/E`, `P/B`, `EV/EBITDA`, `ROE`, `ROCE`, `OPM %`, `Debt-to-Equity`, `Interest Coverage`, `3Y/5Y CAGR`, `Relative Volume`), and `screener.fundamental_data_source` describes delayed EOD and reported corporate filings.
  - Confirm that this list matches the exact columns currently exposed in `https://learninglab.streamlit.app/`.

- [ ] **6. Real Scanner Screenshot (`assets/screener.png`)**
  - No `assets/screener.png` was present in the workspace, so the build uses the clean HTML illustrative output table on `/screener/` and the subtle decorative `hero.webp` background on `/`.
  - If you capture a real screenshot of the Streamlit app, save it at `assets/screener.png` and re-run `python build.py` — the build will automatically embed it with the caption `"Illustrative output"`.

- [ ] **7. Proof-Strip Statistics (`data/site.json` -> `screener.universe_size`, `stats`)**
  - Verify `screener.universe_size` (`"NSE & BSE (8 Universes)"`), `stats.reports_published` (`"3 Case Studies"`), and `stats.cohorts_run` (`"40 Lessons"`). Any field set to `""` will hide that stat automatically.

- [ ] **8. Educational Research Reports (`data/research.json`) & SEBI Compliance Check**
  - Review the 3 mentor-reviewed sample educational case studies in `data/research.json` (marked `<!-- OWNER: review for accuracy -->`).
  - **Compliance action:** As noted in the HTML comment at the top of `/research/` and `/screener/`, confirm your SEBI Research Analyst (Regulations, 2014) position with a qualified compliance professional before publishing company-specific views. Keep all published student reports strictly educational (no target prices, no buy/sell/hold ratings).

- [ ] **9. Blog Guides Accuracy Review (`data/blog.json`)**
  - Review the 9 long-form SEO guides in `/blog/` (all marked `<!-- OWNER: review for accuracy -->`), including the NISM Series VIII exam fee and syllabus notes.

- [ ] **10. Contact Form Endpoint (`build.py` -> `FORM_ENDPOINT_PLACEHOLDER`)**
  - Replace `https://api.web3forms.com/submit` (or Formspree endpoint) on `/contact/` with your live form endpoint or access key.

- [ ] **11. Privacy-Friendly Analytics (`data/site.json` -> `analytics`)**
  - Set `analytics.provider` (`"plausible"` or `"ga4"`) and `analytics.id` (`"harionresearch.co.in"` or `"G-XXXXXXXXXX"`) to start recording `click_open_scanner`, `click_view_internship`, `click_enroll`, and `click_cross_promo`.

- [ ] **12. Proficient Trading Program Decision**
  - Per the build specification, Proficient Trading has been removed as a headline offer and `/proficient-trading-program/*` 301-redirects to `/other-programs/`. Confirm whether you want it kept omitted or mentioned briefly on `/other-programs/`.

- [ ] **13. Testimonials & Institutional Claims Verification (`data/site.json` -> `claims`)**
  - The unverified placement claim ("Aditya secured a Relationship Manager role...") and the unverified "Trusted by IIT, NIT, Delhi University, CUSAT" line have been removed.
  - Only the named Indus Business Academy testimonial (Veda Vyas Harikumar) and the PIBM student project quote (Bhagatsing Patil) are included. Confirm written permission for both.

- [ ] **14. Remove `/_styleguide/` Before Final Launch**
  - `/_styleguide/` is set to `noindex, nofollow` and excluded from `sitemap.xml` and `robots.txt`. Delete `templates/_styleguide/` and re-run `python build.py` when you no longer need the visual reference.

