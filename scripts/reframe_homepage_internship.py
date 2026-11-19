"""
1. Replace Classroom section (section 6) on homepage with Research Reports teaser.
2. Reframe internship page hero kicker.
"""
import pathlib, sys

ROOT = pathlib.Path(__file__).parent.parent

# ── 1. Homepage ───────────────────────────────────────────────────────────────
hp = ROOT / "templates" / "index.html"
html = hp.read_text(encoding="utf-8")

OLD_CLASSROOM = """    <!-- 6. Harion Classroom -->
    <section id="classroom">
      <div class="w">
        <div class="split-grid" style="align-items:center">
          <div>
            <span class="kicker">Self-Paced Portal</span>
            <h2>Learn in the Harion Classroom</h2>
            <p class="lede">40 structured, self-paced lessons that take you step by step through financial statements, sector analysis, and valuation on a real listed company.</p>
            <div class="btn-row">
              <a class="btn" href="https://classroom.harionresearch.co.in">Open the Classroom &rarr;</a>
              <a class="btn btn-equal" href="/equity-research-internship/">About the Internship</a>
            </div>
          </div>
          <div class="card">
            <span class="kicker">Already Enrolled?</span>
            <h3>Continue your 40 lessons</h3>
            <p>Sign in at <a href="https://classroom.harionresearch.co.in">classroom.harionresearch.co.in</a> to resume your self-paced modules, access weekly review material, and submit your equity research report.</p>
            <p class="quiet-note">Need another program? See <a href="/other-programs/">NISM Series VIII &amp; Portfolio Manager Programs</a>.</p>
          </div>
        </div>
      </div>
    </section>"""

NEW_RESEARCH = """    <!-- 6. Research output -->
    <section id="research-output">
      <div class="w">
        <div class="section-head">
          <div>
            <span class="kicker">Research Output</span>
            <h2>What our analysts publish</h2>
          </div>
          <a class="mono" style="font-size:0.875rem" href="/research/">All reports &rarr;</a>
        </div>
        <p class="lede">Mentor-reviewed educational case studies produced inside the Harion analytical workflow — real companies, real filings, structured methodology.</p>
        <div class="open-cols">
          <div class="open-col">
            <span class="open-col-num">IT Services</span>
            <h3>Operating Margins &amp; Cash Conversion</h3>
            <p>Comparing utilisation, deal mix and free-cash-flow conversion across Indian IT services companies.</p>
            <a class="mono" style="font-size:0.875rem" href="/research/indian-it-services-sector-margin-and-cashflow-study/">Read case study &rarr;</a>
          </div>
          <div class="open-col">
            <span class="open-col-num">Industrials</span>
            <h3>Working Capital &amp; ROCE Decomposition</h3>
            <p>DuPont analysis and cash-conversion cycles across capital-intensive Indian manufacturing businesses.</p>
            <a class="mono" style="font-size:0.875rem" href="/research/working-capital-and-roce-in-indian-manufacturing/">Read case study &rarr;</a>
          </div>
          <div class="open-col">
            <span class="open-col-num">Cross-Sector</span>
            <h3>Balance-Sheet Leverage &amp; Interest Coverage</h3>
            <p>A structured framework for studying debt, coverage ratios and solvency across NSE and BSE universes.</p>
            <a class="mono" style="font-size:0.875rem" href="/research/reading-leverage-and-interest-coverage-across-cycles/">Read case study &rarr;</a>
          </div>
        </div>
      </div>
    </section>"""

if OLD_CLASSROOM not in html:
    print("ERROR: Classroom section not found in index.html — check whitespace/CRLF")
    sys.exit(1)

html = html.replace(OLD_CLASSROOM, NEW_RESEARCH)
hp.write_text(html, encoding="utf-8")
print("Homepage: Classroom section replaced with Research Output section.")

# ── 2. Internship page hero kicker ───────────────────────────────────────────
ip = ROOT / "templates" / "equity-research-internship" / "index.html"
ihtml = ip.read_text(encoding="utf-8")

OLD_KICKER = '<span class="kicker">Flagship Training Program &middot; Online India</span>'
NEW_KICKER = '<span class="kicker">Research Analyst Training &middot; Built on the Harion Scanner</span>'

if OLD_KICKER not in ihtml:
    print("ERROR: Internship kicker not found — check exact string")
    sys.exit(1)

ihtml = ihtml.replace(OLD_KICKER, NEW_KICKER)
ip.write_text(ihtml, encoding="utf-8")
print("Internship page: hero kicker reframed.")

print("All done.")
