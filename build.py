#!/usr/bin/env python3
"""
Static build script for Harion Research website (Python 3 stdlib only).
Reads JSON data from data/*.json, renders HTML templates in templates/,
generates research and blog pages, and writes complete static files to dist/
and syncs to workspace root for immediate local preview.
"""

import html
import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT / "data"
TEMPLATES_DIR = ROOT / "templates"
DIST_DIR = ROOT / "dist"

SITE_EMAIL_PLACEHOLDER = "info@harionresearch.co.in"
GRIEVANCE_NAME_PLACEHOLDER = "Abhilash Bhoyar"
FORM_ENDPOINT_PLACEHOLDER = "https://api.web3forms.com/submit"
LASTMOD_DATE = "2026-10-31"

DISCLAIMER_TEXT = (
    "Harion Research is a financial education and research platform. "
    "We do not provide investment advisory, portfolio management, trade execution, "
    "or trading recommendations. All tools, content, webinars, and programs are "
    "intended solely for educational, research, and informational purposes and "
    "should not be construed as financial advice or used for investment "
    "decision-making. Data is delayed and may contain errors."
)


def load_json(name: str) -> dict:
    path = DATA_DIR / name
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def esc(val: str) -> str:
    return html.escape(str(val or ""), quote=True)


def tbc(val: str) -> str:
    v = str(val or "").strip()
    return esc(v) if v else "TBC"


def get_email(site: dict) -> str:
    raw = str(site.get("entity", {}).get("email", "")).strip()
    return raw if raw else SITE_EMAIL_PLACEHOLDER


def get_grievance_name(site: dict) -> str:
    raw = str(site.get("grievance_officer", {}).get("name", "")).strip()
    return raw if raw else GRIEVANCE_NAME_PLACEHOLDER


def get_grievance_email(site: dict) -> str:
    raw = str(site.get("grievance_officer", {}).get("email", "")).strip()
    return raw if raw else get_email(site)


def render_analytics(site: dict) -> str:
    analytics = site.get("analytics", {})
    provider = str(analytics.get("provider", "")).strip().lower()
    aid = str(analytics.get("id", "")).strip()
    if not provider or not aid:
        return ""
    if provider == "plausible":
        return f'<script defer data-domain="{esc(aid)}" src="https://plausible.io/js/script.js"></script>'
    if provider in ("ga4", "gtag", "google"):
        return (
            f'<script async src="https://www.googletagmanager.com/gtag/js?id={esc(aid)}"></script>'
            f"<script>window.dataLayer=window.dataLayer||[];function gtag(){{dataLayer.push(arguments);}}gtag('js',new Date());gtag('config','{esc(aid)}');</script>"
        )
    if provider == "cloudflare":
        return f'<script defer src="https://static.cloudflareinsights.com/beacon.min.js" data-cf-beacon=\'{{"token": "{esc(aid)}"}}\'></script>'
    if provider == "clarity":
        return (
            "<script type=\"text/javascript\">"
            "(function(c,l,a,r,i,t,y){c[a]=c[a]||function(){(c[a].q=c[a].q||[]).push(arguments)};"
            f"t=l.createElement(r);t.async=1;t.src=\"https://www.clarity.ms/tag/\"+i;y=l.getElementsByTagName(r)[0];y.parentNode.insertBefore(t,y);}})(window, document, \"clarity\", \"script\", \"{esc(aid)}\");"
            "</script>"
        )
    return ""


def render_header(site: dict, active_path: str = "/") -> str:
    nav_items = [
        ("/equity-research-internship/", "Internship"),
        ("/screener/", "Screener"),
        ("/careers/", "Careers"),
        ("/blog/", "Blog"),
        ("/about/", "About"),
    ]
    links_html = []
    for href, label in nav_items:
        is_active = active_path == href or (href != "/" and active_path.startswith(href))
        current = ' aria-current="page"' if is_active else ""
        links_html.append(f'<li><a href="{href}"{current}>{esc(label)}</a></li>')

    return (
        '<header class="site-header">'
        '<div class="w bar">'
        '<a class="logo-link" href="/">'
        '<picture>'
        '<source srcset="/assets/logo.webp" type="image/webp">'
        '<img src="/assets/logo.png" alt="Harion Research" width="130" height="46">'
        '</picture>'
        '</a>'
        '<input type="checkbox" id="nav-toggle" class="nav-toggle-input">'
        '<label for="nav-toggle" class="burger" aria-label="Toggle navigation menu" aria-expanded="false">&#9776;</label>'
        '<nav class="site-nav" aria-label="Primary navigation">'
        f'<ul class="nav-links">{"".join(links_html)}</ul>'
        '<div class="nav-actions">'
        '<a class="btn btn-sm" href="https://classroom.harionresearch.co.in">Classroom &rarr;</a>'
        '</div>'
        '</nav>'
        '</div>'
        '</header>'
    )


def render_footer(site: dict) -> str:
    ent = site.get("entity", {})
    name = ent.get("name", "Harion Research")
    addr = ent.get("address", "3rd Floor, Silver Sanchora, R.N.T. Marg, Indore, Madhya Pradesh 452001")
    phone = ent.get("phone", "+91-7067000393")
    email = get_email(site)
    udyam = ent.get("udyam", "UDYAM-MP-22-0035155")
    prog = site.get("program", {})
    prog_name = prog.get("name", "Equity Research Internship Program")
    prog_dur = tbc(prog.get("duration", ""))
    prog_price = tbc(prog.get("price", ""))
    screener_url = site.get("screener", {}).get("url", "https://learninglab.streamlit.app/")

    return (
        '<footer class="site-footer">'
        '<div class="w">'
        '<div class="footer-grid">'
        '<div class="footer-col">'
        f'<span class="footer-col-title">{esc(name)}</span>'
        '<p>Harion Research is a financial education and research platform.</p>'
        f'<p>{esc(addr)}<br>{esc(phone)}<br><a href="mailto:{esc(email)}" style="color:#D1D5DB">{esc(email)}</a></p>'
        '</div>'
        '<div class="footer-col">'
        '<span class="footer-col-title">Research &amp; Tools</span>'
        '<ul class="footer-links">'
        '<li><a href="/screener/">Market Analysis Learning Lab</a></li>'
        f'<li><a href="{esc(screener_url)}" data-event="click_open_scanner">Open the Research Scanner</a></li>'
        '<li><a href="/methodology/">Methodology</a></li>'
        '<li><a href="/research/">Educational Research Reports</a></li>'
        '<li><a href="https://classroom.harionresearch.co.in">Harion Classroom</a></li>'
        '</ul>'
        '</div>'
        '<div class="footer-col">'
        '<span class="footer-col-title">Programs</span>'
        '<ul class="footer-links">'
        f'<li><a href="/equity-research-internship/">{esc(prog_name)}</a></li>'
        '<li><a href="/other-programs/#portfolio-manager">Portfolio Manager Program</a></li>'
        '<li><a href="/other-programs/#nism-series-viii">NISM Series VIII Preparation</a></li>'
        '<li><a href="/equity-research-internship/#join-the-lab">Join the Lab</a></li>'
        '</ul>'
        '</div>'
        '<div class="footer-col">'
        '<span class="footer-col-title">Company &amp; Policies</span>'
        '<ul class="footer-links">'
        '<li><a href="/about/">About</a></li>'
        '<li><a href="/careers/">Careers in Finance Guide</a></li>'
        '<li><a href="/blog/">Blog &amp; Guides</a></li>'
        '<li><a href="/faq/">FAQ</a></li>'
        '<li><a href="/contact/">Contact</a></li>'
        '<li><a href="/privacy-policy/">Privacy Policy</a></li>'
        '<li><a href="/terms/">Terms of Service</a></li>'
        '<li><a href="/refund-policy/">Refund Policy</a></li>'
        '</ul>'
        '</div>'
        '</div>'
        '<div class="footer-legal">'
        f'<p>{esc(DISCLAIMER_TEXT)}</p>'
        f'<p>&copy; 2026 {esc(name)}. Udyam Registration: <span class="mono">{esc(udyam)}</span></p>'
        '</div>'
        '</div>'
        '</footer>'
    )


def render_proof_strip(site: dict) -> str:
    screener = site.get("screener", {})
    stats_obj = site.get("stats", {})
    filters_list = screener.get("fundamental_filters") or []

    candidates = [
        (str(screener.get("universe_size", "")).strip(), "Market universes in scanner (EOD)"),
        (f"{len(filters_list)} Metrics" if len(filters_list) > 0 else "", "Fundamental & price study filters"),
        (str(stats_obj.get("reports_published", "")).strip(), "Educational learning reports"),
        (str(stats_obj.get("cohorts_run", "")).strip(), "Structured classroom curriculum"),
    ]
    non_empty = [(v, lbl) for (v, lbl) in candidates if v]
    if not non_empty:
        return ""

    items = []
    for val, label in non_empty:
        items.append(
            '<div class="stat-item">'
            f'<span class="stat-val">{esc(val)}</span>'
            f'<span class="stat-label">{esc(label)}</span>'
            '</div>'
        )
    return (
        '<section class="proof-strip" aria-label="Platform statistics">'
        f'<div class="w"><div class="stat-grid">{"".join(items)}</div></div>'
        '</section>'
    )


def render_research_list(research: dict, limit: int = 0) -> str:
    reports = research.get("reports", [])
    if not reports:
        return (
            '<div class="empty-notice">'
            '<span>First learning reports publishing soon.</span>'
            '<a class="mono" style="font-size:0.875rem" href="/methodology/">Review our research methodology &rarr;</a>'
            '</div>'
        )
    subset = reports[:limit] if limit > 0 else reports
    items = []
    for r in subset:
        slug = esc(r.get("slug", ""))
        title = esc(r.get("title", ""))
        date = esc(r.get("date", ""))
        tag = esc(r.get("tag", "Educational Case Study"))
        summary = esc(r.get("summary", ""))
        items.append(
            '<li class="ruled-item">'
            f'<div class="ruled-meta">{date}<br><span class="tag tag-teal" style="margin-top:6px">{tag}</span></div>'
            f'<div class="ruled-body"><h3><a href="/research/{slug}/">{title}</a></h3><p>{summary}</p></div>'
            f'<div><a class="mono" style="font-size:0.875rem" href="/research/{slug}/">Read &rarr;</a></div>'
            '</li>'
        )
    return f'<ul class="ruled-list">{"".join(items)}</ul>'


def render_blog_list(blog: dict) -> str:
    posts = blog.get("posts", [])
    if not posts:
        return ""
    items = []
    for p in posts:
        slug = esc(p.get("slug", ""))
        title = esc(p.get("h1", ""))
        date = esc(p.get("date", ""))
        cat = esc(p.get("category", "Guide"))
        summary = esc(p.get("summary", ""))
        items.append(
            '<li class="ruled-item">'
            f'<div class="ruled-meta">{date}<br><span class="tag" style="margin-top:6px">{cat}</span></div>'
            f'<div class="ruled-body"><h3><a href="/blog/{slug}/">{title}</a></h3><p>{summary}</p></div>'
            f'<div><a class="mono" style="font-size:0.875rem" href="/blog/{slug}/">Read guide &rarr;</a></div>'
            '</li>'
        )
    return f'<ul class="ruled-list">{"".join(items)}</ul>'


def render_screener_preview_home() -> str:
    screener_png = ROOT / "assets" / "screener.png"
    if screener_png.exists():
        return (
            '<figure class="card" style="margin:16px 0 24px;padding:12px">'
            '<img src="/assets/screener.png" alt="Market Analysis Learning Lab illustrative output" width="520" height="320" loading="lazy">'
            '<figcaption class="mono muted" style="font-size:0.75rem;margin-top:8px">Illustrative output</figcaption>'
            '</figure>'
        )
    return (
        '<ul class="spec-list" style="margin:24px 0">'
        '<li><span>NSE Universes</span><strong>NIFTY 50, NIFTY 200, NIFTY 500, All NSE</strong></li>'
        '<li><span>BSE Universes</span><strong>Large Cap, Mid Cap, Small Cap, All BSE</strong></li>'
        '<li><span>Price &amp; Volume Lenses</span><strong>Range structure, moving averages, relative volume</strong></li>'
        '<li><span>Fundamental Filters</span><strong>P/E, P/B, EV/EBITDA, ROE, ROCE, OPM %, D/E</strong></li>'
        '<li><span>Data Feed</span><strong>Delayed End-of-Day (case-study observation)</strong></li>'
        '</ul>'
    )


def render_fundamental_filters_block(site: dict) -> str:
    filters = site.get("screener", {}).get("fundamental_filters") or []
    if not filters:
        return ""
    tags = [f'<span class="tag tag-teal">{esc(f.get("name", ""))}</span>' for f in filters if f.get("name")]
    return (
        '<div style="margin-top:40px;padding-top:24px;border-top:1px solid var(--border)">'
        '<span class="kicker">Configured Scanner Study Filters</span>'
        '<p style="margin-bottom:12px">The Research Scanner currently includes the following fundamental and market-structure study metrics for comparing companies within a dataset:</p>'
        f'<div style="display:flex;flex-wrap:wrap;gap:8px">{"".join(tags)}</div>'
        '</div>'
    )


def render_fundamental_data_source_note(site: dict) -> str:
    src = str(site.get("screener", {}).get("fundamental_data_source", "")).strip()
    if not src:
        return ""
    return f'<p class="quiet-note" style="margin-top:16px"><strong>Fundamental data:</strong> {esc(src)}.</p>'


def render_screener_illustrative_block() -> str:
    screener_png = ROOT / "assets" / "screener.png"
    if screener_png.exists():
        return (
            '<figure class="card" style="margin:16px 0;padding:12px">'
            '<img src="/assets/screener.png" alt="Market Analysis Learning Lab illustrative output" width="520" height="320" loading="lazy">'
            '<figcaption class="mono muted" style="font-size:0.75rem;margin-top:8px">Illustrative output</figcaption>'
            '</figure>'
        )
    return (
        '<div class="table-wrap" style="margin-top:16px">'
        '<table class="data-table" aria-label="Illustrative scanner output table">'
        '<thead>'
        '<tr>'
        '<th>Study Entity (Anonymized)</th>'
        '<th>Universe</th>'
        '<th>ROCE %</th>'
        '<th>OPM %</th>'
        '<th>Debt / Equity</th>'
        '<th>Trailing P/E</th>'
        '</tr>'
        '</thead>'
        '<tbody>'
        '<tr>'
        '<td class="mono">Case Study A (IT Services)</td>'
        '<td>NIFTY 50</td>'
        '<td class="mono">38.4%</td>'
        '<td class="mono">24.1%</td>'
        '<td class="mono">0.08</td>'
        '<td class="mono">26.5x</td>'
        '</tr>'
        '<tr>'
        '<td class="mono">Case Study B (Industrial Mfg)</td>'
        '<td>NIFTY 200</td>'
        '<td class="mono">19.2%</td>'
        '<td class="mono">14.8%</td>'
        '<td class="mono">0.35</td>'
        '<td class="mono">31.0x</td>'
        '</tr>'
        '<tr>'
        '<td class="mono">Case Study C (Process Mfg)</td>'
        '<td>BSE Mid Cap</td>'
        '<td class="mono">12.6%</td>'
        '<td class="mono">11.2%</td>'
        '<td class="mono">0.92</td>'
        '<td class="mono">15.4x</td>'
        '</tr>'
        '</tbody>'
        '</table>'
        '</div>'
        '<p class="quiet-note">Illustrative output &middot; Anonymized historical case-study rows showing how fundamental and structure metrics are displayed together.</p>'
    )


def render_changelog_section(changelog: dict) -> str:
    entries = changelog.get("entries", [])
    if not entries:
        return ""
    rows = []
    for e in entries:
        ver = esc(e.get("version", ""))
        dt = esc(e.get("date", ""))
        title = esc(e.get("title", ""))
        summary = esc(e.get("summary", ""))
        rows.append(
            '<li class="ruled-item">'
            f'<div class="ruled-meta">{dt}<br><span class="tag" style="margin-top:6px">{ver}</span></div>'
            f'<div class="ruled-body"><h3>{title}</h3><p>{summary}</p></div>'
            '<div></div>'
            '</li>'
        )
    return (
        '<section class="alt" id="changelog">'
        '<div class="w">'
        '<span class="kicker">09 / Release Notes</span>'
        '<h2>Learning Lab Changelog</h2>'
        f'<ul class="ruled-list">{"".join(rows)}</ul>'
        '</div>'
        '</section>'
    )


def render_methodology_filters_table(site: dict) -> str:
    filters = site.get("screener", {}).get("fundamental_filters") or []
    if not filters:
        return '<p class="muted">Filter definitions are being updated.</p>'
    rows = []
    for f in filters:
        name = esc(f.get("name", ""))
        cat = esc(f.get("category", ""))
        defn = esc(f.get("definition", ""))
        rows.append(
            '<tr>'
            f'<td><strong>{name}</strong></td>'
            f'<td><span class="tag">{cat}</span></td>'
            f'<td>{defn}</td>'
            '</tr>'
        )
    return (
        '<div class="table-wrap">'
        '<table class="data-table">'
        '<thead><tr><th scope="col">Study Metric / Filter</th><th scope="col">Category</th><th scope="col">Definition in Reported Filings</th></tr></thead>'
        f'<tbody>{"".join(rows)}</tbody>'
        '</table>'
        '</div>'
    )


def build_schema_org(site: dict) -> dict:
    ent = site.get("entity", {})
    return {
        "@context": "https://schema.org",
        "@type": "Organization",
        "name": ent.get("name", "Harion Research"),
        "description": "Harion Research is a financial education and research platform.",
        "url": "https://harionresearch.co.in",
        "logo": "https://harionresearch.co.in/assets/logo.png",
        "telephone": ent.get("phone", "+91-7067000393"),
        "email": get_email(site),
        "address": {
            "@type": "PostalAddress",
            "streetAddress": "3rd Floor, Silver Sanchora, R.N.T. Marg",
            "addressLocality": "Indore",
            "addressRegion": "Madhya Pradesh",
            "postalCode": "452001",
            "addressCountry": "IN",
        },
    }


def build_breadcrumb(items: list) -> dict:
    return {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {
                "@type": "ListItem",
                "position": idx + 1,
                "name": name,
                "item": f"https://harionresearch.co.in{url}",
            }
            for idx, (name, url) in enumerate(items)
        ],
    }


def write_out(rel_path: Path, content: str) -> None:
    out_dist = DIST_DIR / rel_path
    out_dist.parent.mkdir(parents=True, exist_ok=True)
    out_dist.write_text(content, encoding="utf-8")


def build() -> None:
    site = load_json("site.json")
    research = load_json("research.json")
    changelog = load_json("changelog.json")
    blog = load_json("blog.json")

    screener_png = ROOT / "assets" / "screener.png"
    has_screener_img = screener_png.exists()

    if has_screener_img:
        hero_grid_class = ""
        hero_decor = ""
        hero_right = (
            '<figure class="card" style="margin:0;padding:16px">'
            '<img src="/assets/screener.png" alt="Harion Research Scanner illustrative output" width="480" height="320">'
            '<figcaption class="mono muted" style="font-size:0.75rem;margin-top:8px">Illustrative output &middot; Market Analysis Learning Lab</figcaption>'
            '</figure>'
        )
    else:
        hero_grid_class = ""
        hero_decor = ""
        hero_right = (
            '<div class="hero-graphic-wrap">'
            '<picture>'
            '<source srcset="/assets/hero.webp" type="image/webp">'
            '<img class="hero-graphic" src="/assets/hero.png" alt="Quantitative market analysis graphic" width="480" height="465" fetchpriority="high">'
            '</picture>'
            '</div>'
        )

    org_schema = build_schema_org(site)
    prog = site.get("program", {})
    ent = site.get("entity", {})
    screener_url = site.get("screener", {}).get("url", "https://learninglab.streamlit.app/")

    schema_home = json.dumps(
        [
            org_schema,
            {
                "@context": "https://schema.org",
                "@type": "WebSite",
                "name": ent.get("name", "Harion Research"),
                "url": "https://harionresearch.co.in",
            },
        ],
        ensure_ascii=False,
    )

    schema_internship = json.dumps(
        [
            org_schema,
            build_breadcrumb([("Home", "/"), ("Equity Research Internship Program", "/equity-research-internship/")]),
            {
                "@context": "https://schema.org",
                "@type": "Course",
                "name": prog.get("name", "Equity Research Internship Program"),
                "description": "Train on the Harion Research Scanner, build a financial statement model, and publish a mentor-reviewed educational equity research report.",
                "provider": {
                    "@type": "Organization",
                    "name": ent.get("name", "Harion Research"),
                    "sameAs": "https://harionresearch.co.in",
                },
                "offers": {
                    "@type": "Offer",
                    "price": "500",
                    "priceCurrency": "INR",
                    "description": tbc(prog.get("price", "")),
                },
            },
            {
                "@context": "https://schema.org",
                "@type": "FAQPage",
                "mainEntity": [
                    {
                        "@type": "Question",
                        "name": "Is this an employment job or an educational training program?",
                        "acceptedAnswer": {
                            "@type": "Answer",
                            "text": "The Harion Equity Research Internship Program is a structured online educational training program where you learn equity research methodology and complete a mentor-reviewed research report on a listed company.",
                        },
                    },
                    {
                        "@type": "Question",
                        "name": "What are the duration and program fee?",
                        "acceptedAnswer": {
                            "@type": "Answer",
                            "text": f"The program duration is {tbc(prog.get('duration', ''))}. The fee structure is {tbc(prog.get('price', ''))}.",
                        },
                    },
                    {
                        "@type": "Question",
                        "name": "Do I need prior experience in financial modelling or coding?",
                        "acceptedAnswer": {
                            "@type": "Answer",
                            "text": "No prior experience is required. The curriculum begins with financial statement foundations and guides you step by step.",
                        },
                    },
                    {
                        "@type": "Question",
                        "name": "Does the program involve live trading or stock recommendations?",
                        "acceptedAnswer": {
                            "@type": "Answer",
                            "text": "No. In compliance with SEBI educational regulations, all analysis uses historical financial filings and delayed market data.",
                        },
                    },
                ],
            },
        ],
        ensure_ascii=False,
    )

    schema_faq = json.dumps(
        [
            org_schema,
            build_breadcrumb([("Home", "/"), ("FAQ", "/faq/")]),
            {
                "@context": "https://schema.org",
                "@type": "FAQPage",
                "mainEntity": [
                    {
                        "@type": "Question",
                        "name": "What is Harion Research?",
                        "acceptedAnswer": {
                            "@type": "Answer",
                            "text": "Harion Research is a financial education and research platform based in Indore, India, building the Market Analysis Learning Lab (Research Scanner) and running the Equity Research Internship Program.",
                        },
                    },
                    {
                        "@type": "Question",
                        "name": "Are the programs suitable for beginners?",
                        "acceptedAnswer": {
                            "@type": "Answer",
                            "text": "Yes. The curriculum starts with financial statement and market structure foundations and progresses step by step to building a company model and writing a full equity research report.",
                        },
                    },
                    {
                        "@type": "Question",
                        "name": "Do you use live market data or provide trading recommendations?",
                        "acceptedAnswer": {
                            "@type": "Answer",
                            "text": "No. Live discussions use historical market data and reported company filings, and the Research Scanner runs on delayed End-of-Day data. We provide no investment advice or recommendations.",
                        },
                    },
                ],
            },
        ],
        ensure_ascii=False,
    )

    base_tokens = {
        "{{SITE_EMAIL}}": esc(get_email(site)),
        "{{SITE_PHONE}}": esc(ent.get("phone", "+91-7067000393")),
        "{{SITE_ADDRESS}}": esc(ent.get("address", "")),
        "{{SITE_UDYAM}}": esc(ent.get("udyam", "UDYAM-MP-22-0035155")),
        "{{GRIEVANCE_NAME}}": esc(get_grievance_name(site)),
        "{{GRIEVANCE_EMAIL}}": esc(get_grievance_email(site)),
        "{{FORM_ENDPOINT}}": esc(FORM_ENDPOINT_PLACEHOLDER),
        "{{DISCLAIMER}}": esc(DISCLAIMER_TEXT),
        "{{SCREENER_URL}}": esc(screener_url),
        "{{PROGRAM_NAME}}": esc(prog.get("name", "Equity Research Internship Program")),
        "{{PROGRAM_DURATION}}": tbc(prog.get("duration", "")),
        "{{PROGRAM_PRICE}}": tbc(prog.get("price", "")),
        "{{PROGRAM_FORMAT}}": tbc(prog.get("format", "")),
        "{{PROGRAM_CERTIFICATE}}": tbc(prog.get("certificate", "")),
        "{{PROGRAM_ENROLL_URL}}": esc(prog.get("enroll_url", "https://forms.gle/W7Z35ztDgFDvcWj87")),
        "{{HERO_GRID_CLASS}}": hero_grid_class,
        "{{HERO_DECOR}}": hero_decor,
        "{{HERO_RIGHT}}": hero_right,
        "{{PROOF_STRIP}}": render_proof_strip(site),
        "{{RESEARCH_LIST_HOME}}": render_research_list(research, limit=3),
        "{{RESEARCH_LIST_FULL}}": render_research_list(research, limit=0),
        "{{BLOG_LIST_FULL}}": render_blog_list(blog),
        "{{SCREENER_PREVIEW_HOME}}": render_screener_preview_home(),
        "{{FUNDAMENTAL_FILTERS_BLOCK}}": render_fundamental_filters_block(site),
        "{{FUNDAMENTAL_DATA_SOURCE_NOTE}}": render_fundamental_data_source_note(site),
        "{{SCREENER_ILLUSTRATIVE_BLOCK}}": render_screener_illustrative_block(),
        "{{CHANGELOG_SECTION}}": render_changelog_section(changelog),
        "{{METHODOLOGY_FILTERS_TABLE}}": render_methodology_filters_table(site),
        "{{SCHEMA_HOME}}": schema_home,
        "{{SCHEMA_INTERNSHIP}}": schema_internship,
        "{{SCHEMA_SCREENER}}": json.dumps([org_schema, build_breadcrumb([("Home", "/"), ("Market Analysis Learning Lab", "/screener/")])], ensure_ascii=False),
        "{{SCHEMA_METHODOLOGY}}": json.dumps([org_schema, build_breadcrumb([("Home", "/"), ("Methodology", "/methodology/")])], ensure_ascii=False),
        "{{SCHEMA_RESEARCH_INDEX}}": json.dumps([org_schema, build_breadcrumb([("Home", "/"), ("Research", "/research/")])], ensure_ascii=False),
        "{{SCHEMA_OTHER_PROGRAMS}}": json.dumps([org_schema, build_breadcrumb([("Home", "/"), ("Programs", "/other-programs/")])], ensure_ascii=False),
        "{{SCHEMA_ABOUT}}": json.dumps([org_schema, build_breadcrumb([("Home", "/"), ("About", "/about/")])], ensure_ascii=False),
        "{{SCHEMA_CONTACT}}": json.dumps([org_schema, build_breadcrumb([("Home", "/"), ("Contact", "/contact/")])], ensure_ascii=False),
        "{{SCHEMA_FAQ}}": schema_faq,
        "{{SCHEMA_PRIVACY}}": json.dumps([org_schema, build_breadcrumb([("Home", "/"), ("Privacy Policy", "/privacy-policy/")])], ensure_ascii=False),
        "{{SCHEMA_TERMS}}": json.dumps([org_schema, build_breadcrumb([("Home", "/"), ("Terms of Service", "/terms/")])], ensure_ascii=False),
        "{{SCHEMA_REFUND}}": json.dumps([org_schema, build_breadcrumb([("Home", "/"), ("Refund Policy", "/refund-policy/")])], ensure_ascii=False),
        "{{SCHEMA_BLOG_INDEX}}": json.dumps([org_schema, build_breadcrumb([("Home", "/"), ("Blog", "/blog/")])], ensure_ascii=False),
        "{{SCHEMA_CAREERS}}": json.dumps([org_schema, build_breadcrumb([("Home", "/"), ("Careers in Finance", "/careers/")])], ensure_ascii=False),
        "{{ANALYTICS_SCRIPT}}": render_analytics(site),
        "{{ FOOTER }}": render_footer(site),
        "{{FOOTER}}": render_footer(site),
    }

    if DIST_DIR.exists():
        shutil.rmtree(DIST_DIR)
    DIST_DIR.mkdir(parents=True, exist_ok=True)

    # Copy assets to dist/assets
    dist_assets = DIST_DIR / "assets"
    dist_assets.mkdir(parents=True, exist_ok=True)
    for asset_file in (ROOT / "assets").iterdir():
        if asset_file.is_file():
            shutil.copy2(asset_file, dist_assets / asset_file.name)

    # Ensure favicon.ico is also available at domain root
    root_ico = ROOT / "assets" / "favicon.ico"
    if root_ico.exists():
        shutil.copy2(root_ico, DIST_DIR / "favicon.ico")
        shutil.copy2(root_ico, ROOT / "favicon.ico")

    # 1. Render standard page templates (skipping _*.html partials)
    for tpl_path in TEMPLATES_DIR.rglob("*.html"):
        if tpl_path.name.startswith("_"):
            continue
        rel = tpl_path.relative_to(TEMPLATES_DIR)
        route = "/" if str(rel) == "index.html" else f"/{rel.parent.as_posix()}/"
        content = tpl_path.read_text(encoding="utf-8")

        tokens = dict(base_tokens)
        tokens["{{HEADER}}"] = render_header(site, active_path=route)
        for k, v in tokens.items():
            content = content.replace(k, v)

        write_out(rel, content)

    # 2. Render individual Research Reports from data/research.json
    report_tpl_path = TEMPLATES_DIR / "research" / "_report.html"
    if report_tpl_path.exists():
        report_tpl = report_tpl_path.read_text(encoding="utf-8")
        for r in research.get("reports", []):
            slug = r.get("slug", "").strip()
            if not slug:
                continue
            sec_html = []
            for s in r.get("sections", []):
                sec_html.append(f'<h2>{esc(s.get("heading", ""))}</h2><p>{esc(s.get("body", ""))}</p>')

            r_schema = json.dumps(
                [
                    org_schema,
                    build_breadcrumb([("Home", "/"), ("Research", "/research/"), (r.get("title", ""), f"/research/{slug}/")]),
                    {
                        "@context": "https://schema.org",
                        "@type": "Article",
                        "headline": r.get("title", ""),
                        "description": r.get("summary", ""),
                        "datePublished": r.get("date", LASTMOD_DATE),
                        "dateModified": r.get("date", LASTMOD_DATE),
                        "author": {"@type": "Organization", "name": "Harion Research"},
                        "publisher": {
                            "@type": "Organization",
                            "name": "Harion Research",
                            "logo": {"@type": "ImageObject", "url": "https://harionresearch.co.in/assets/logo.png"},
                        },
                        "mainEntityOfPage": f"https://harionresearch.co.in/research/{slug}/",
                    },
                ],
                ensure_ascii=False,
            )

            content = report_tpl
            tokens = dict(base_tokens)
            tokens.update(
                {
                    "{{HEADER}}": render_header(site, active_path=f"/research/{slug}/"),
                    "{{REPORT_SLUG}}": esc(slug),
                    "{{REPORT_TITLE}}": esc(r.get("title", "")),
                    "{{REPORT_SEO_TITLE}}": esc(r.get("seo_title", f"{r.get('title', '')} | Harion Research")),
                    "{{REPORT_META_DESC}}": esc(r.get("meta_desc", r.get("summary", ""))),
                    "{{REPORT_SUMMARY}}": esc(r.get("summary", "")),
                    "{{REPORT_DATE}}": esc(r.get("date", "")),
                    "{{REPORT_TAG}}": esc(r.get("tag", "Educational Case Study")),
                    "{{REPORT_AUTHOR}}": esc(r.get("author", "Harion Research Learning Lab")),
                    "{{REPORT_POSITIONS}}": esc(r.get("positions", "No position disclosed.")),
                    "{{REPORT_BODY_SECTIONS}}": "\n".join(sec_html),
                    "{{REPORT_SCHEMA}}": r_schema,
                }
            )
            for k, v in tokens.items():
                content = content.replace(k, v)

            write_out(Path("research") / slug / "index.html", content)

    # 3. Render Blog Posts from data/blog.json
    post_tpl_path = TEMPLATES_DIR / "blog" / "_post.html"
    posts = blog.get("posts", [])
    post_by_slug = {p.get("slug"): p for p in posts}
    if post_tpl_path.exists():
        post_tpl = post_tpl_path.read_text(encoding="utf-8")
        for p in posts:
            slug = p.get("slug", "").strip()
            if not slug:
                continue
            body_parts = []
            for heading, paragraphs in p.get("sections", []):
                body_parts.append(f"<h2>{esc(heading)}</h2>")
                for para in paragraphs:
                    body_parts.append(f"<p>{esc(para)}</p>")

            rel_links = []
            for r_slug in p.get("related", []):
                rp = post_by_slug.get(r_slug)
                if rp:
                    rel_links.append(f'<li><a href="/blog/{esc(r_slug)}/">{esc(rp.get("h1", r_slug))}</a></li>')
            rel_html = f'<ul class="plain-list">{"".join(rel_links)}</ul>' if rel_links else ""

            p_schema = json.dumps(
                [
                    org_schema,
                    build_breadcrumb([("Home", "/"), ("Blog", "/blog/"), (p.get("h1", ""), f"/blog/{slug}/")]),
                    {
                        "@context": "https://schema.org",
                        "@type": "Article",
                        "headline": p.get("h1", ""),
                        "description": p.get("meta_desc", ""),
                        "datePublished": p.get("date", LASTMOD_DATE),
                        "dateModified": p.get("date", LASTMOD_DATE),
                        "author": {"@type": "Organization", "name": "Harion Research"},
                        "publisher": {
                            "@type": "Organization",
                            "name": "Harion Research",
                            "logo": {"@type": "ImageObject", "url": "https://harionresearch.co.in/assets/logo.png"},
                        },
                        "mainEntityOfPage": f"https://harionresearch.co.in/blog/{slug}/",
                    },
                ],
                ensure_ascii=False,
            )

            content = post_tpl
            tokens = dict(base_tokens)
            tokens.update(
                {
                    "{{HEADER}}": render_header(site, active_path=f"/blog/{slug}/"),
                    "{{POST_SLUG}}": esc(slug),
                    "{{POST_TITLE_TAG}}": esc(p.get("title_tag", "")),
                    "{{POST_META_DESC}}": esc(p.get("meta_desc", "")),
                    "{{POST_H1}}": esc(p.get("h1", "")),
                    "{{POST_SUMMARY}}": esc(p.get("summary", "")),
                    "{{POST_CATEGORY}}": esc(p.get("category", "Guide")),
                    "{{POST_DATE}}": esc(p.get("date", LASTMOD_DATE)),
                    "{{POST_READ_TIME}}": esc(p.get("read_time", "8 min read")),
                    "{{POST_BODY_HTML}}": "\n".join(body_parts),
                    "{{POST_RELATED_HTML}}": rel_html,
                    "{{POST_SCHEMA}}": p_schema,
                }
            )
            for k, v in tokens.items():
                content = content.replace(k, v)

            write_out(Path("blog") / slug / "index.html", content)

    # 4. Generate sitemap.xml, robots.txt, _redirects, _headers
    canonical_paths = [
        "/",
        "/screener/",
        "/equity-research-internship/",
        "/careers/",
        "/methodology/",
        "/research/",
        "/other-programs/",
        "/about/",
        "/contact/",
        "/faq/",
        "/blog/",
        "/privacy-policy/",
        "/terms/",
        "/refund-policy/",
    ]
    for r in research.get("reports", []):
        if r.get("slug"):
            canonical_paths.append(f"/research/{r['slug']}/")
    for p in posts:
        if p.get("slug"):
            canonical_paths.append(f"/blog/{p['slug']}/")

    url_entries = []
    for cp in canonical_paths:
        url_entries.append(f"  <url><loc>https://harionresearch.co.in{cp}</loc><lastmod>{LASTMOD_DATE}</lastmod></url>")
    sitemap_xml = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + "\n".join(url_entries)
        + "\n</urlset>\n"
    )
    write_out(Path("sitemap.xml"), sitemap_xml)

    robots_txt = "User-agent: *\nAllow: /\nSitemap: https://harionresearch.co.in/sitemap.xml\n"
    write_out(Path("robots.txt"), robots_txt)

    redirects_txt = (
        "/portfolio-manager-internship/* /other-programs/#portfolio-manager 301\n"
        "/nism-series-viii-course/* /other-programs/#nism-series-viii 301\n"
        "/proficient-trading-program/* /other-programs/ 301\n"
    )
    write_out(Path("_redirects"), redirects_txt)

    headers_txt = (
        "/*\n"
        "  X-Content-Type-Options: nosniff\n"
        "  X-Frame-Options: DENY\n"
        "  Referrer-Policy: strict-origin-when-cross-origin\n"
        "  Permissions-Policy: camera=(), microphone=(), geolocation=()\n"
        "\n"
        "/assets/*\n"
        "  Cache-Control: public, max-age=31536000, immutable\n"
    )
    write_out(Path("_headers"), headers_txt)

    print(f"Build complete: {len(canonical_paths)} canonical pages generated in dist/.")


if __name__ == "__main__":
    build()
