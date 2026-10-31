# Harion Research Website

Static HTML/CSS/JS website for **Harion Research** (`https://harionresearch.co.in`), an Indian financial education and research platform. Built with zero frameworks and a Python 3 standard-library static generator (`build.py`) for deployment to **Cloudflare Pages**.

---

## Directory Structure

```text
harion-research-site/
├── assets/
│   ├── style.css          # Editorial / research-journal design system
│   ├── site.js            # Progressive enhancement (mobile nav, form honeypot, analytics events)
│   ├── logo.png / .webp   # Harion Research brand logo
│   └── hero.png / .webp   # Subtle decorative background graphic
├── data/
│   ├── site.json          # Single source of truth: entity, program fee/duration, scanner filters, stats
│   ├── research.json      # Educational case studies / learning reports
│   ├── changelog.json     # Market Analysis Learning Lab release notes
│   └── blog.json          # Long-form student & exam guides
├── templates/             # HTML templates with {{TOKEN}} placeholders
├── dist/                  # Complete static production output (Cloudflare Pages publish directory)
├── docs/
│   └── OFFSITE-SEO.md     # Off-site SEO & distribution playbook
├── build.py               # Zero-dependency Python 3 build script
├── _redirects             # Cloudflare Pages 301 redirect rules
├── _headers               # Security and asset caching headers
├── sitemap.xml            # Auto-generated XML sitemap with lastmod
├── robots.txt             # Crawler directives
└── TODO-FOR-OWNER.md      # Actionable checklist of owner confirmations before production launch
```

---

## 1. Editing Site Content (`data/*.json`)

All key figures, contact details, program fees, scanner filter definitions, and articles live in `data/`:

- **`data/site.json`**
  - `entity`: Legal name, Udyam registration (`UDYAM-MP-22-0035155`), official email, phone, and Indore office address.
  - `grievance_officer`: Name and email displayed on `/contact/` and in `/privacy-policy/`, `/terms/`, and `/refund-policy/`.
  - `program`: Name (`Equity Research Internship Program`), `price`, `duration`, `format`, `certificate`, and `enroll_url`. Updating these fields updates the Homepage, Internship page, Blog callouts, Footer, and Legal Policies simultaneously. (If left empty `""`, the build safely renders `TBC`.)
  - `screener`: Streamlit URL, `universe_size`, `fundamental_data_source`, and `fundamental_filters` (rendered on `/screener/` and `/methodology/`).
  - `stats`: `reports_published` and `cohorts_run` for the homepage proof strip (empty values hide automatically).
  - `analytics`: Set `provider` to `"plausible"` or `"ga4"` and `id` to your domain or Measurement ID (`G-XXXXXXX`) to enable event tracking (`click_open_scanner`, `click_view_internship`, `click_enroll`, `click_cross_promo`).
- **`data/research.json`**: Add or edit educational case studies. Each entry generates `/research/<slug>/index.html` and updates `/research/` and the homepage.
- **`data/changelog.json`**: Add release notes for the Market Analysis Learning Lab (`/screener/#changelog`).
- **`data/blog.json`**: Add or edit long-form student guides (`/blog/<slug>/index.html`).

---

## 2. Running the Build & Local Preview

No `npm` or third-party Python packages are required. Run:

```bash
python build.py
```

`build.py` stamps all templates with data from `data/*.json`, writes the production site to `dist/`, and syncs the generated pages to the workspace root.

To preview locally on port `8000`:

```bash
python -m http.server 8000
```

Then open `http://localhost:8000/`.

---

## 3. Deploying to Cloudflare Pages

### Option A: Direct Git Integration (Recommended)
1. Push this repository to GitHub or GitLab.
2. In the **Cloudflare Dashboard**, go to **Workers & Pages -> Create application -> Pages -> Connect to Git**.
3. Configure the build settings:
   - **Framework preset:** `None`
   - **Build command:** `python3 build.py`
   - **Build output directory:** `dist`
4. Before final production launch, delete `templates/_styleguide/` (and `dist/_styleguide/`) or keep it blocked via `robots.txt` (`Disallow: /_styleguide/`).

### Option B: Wrangler CLI Upload
```bash
python build.py
npx wrangler pages deploy dist --project-name=harion-research
```

