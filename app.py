import json
import os
import hashlib
import csv
import io
import xml.etree.ElementTree as ET
import mimetypes
from datetime import datetime, timezone
from html import escape
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, quote_plus, unquote, urlparse
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError
import secrets


HOST = os.environ.get("HOST", "127.0.0.1")
PORT = int(os.environ.get("PORT", "8000"))
SITE_NAME = "Niharika Wholesale"
COURSERA_BLOG_FEED = os.environ.get("COURSERA_BLOG_FEED", "https://blog.coursera.org/feed/")
MONTHLY_PRICE_INR = 500
RAZORPAY_SUBSCRIPTION_LINK = os.environ.get("RAZORPAY_SUBSCRIPTION_LINK", "")
BHIM_UPI_ID = os.environ.get("NIHARIKA_UPI_ID") or os.environ.get("BHIM_UPI_ID", "")
NIHARIKA_PAYMENT_PHONE = "".join(ch for ch in os.environ.get("NIHARIKA_PAYMENT_PHONE", "") if ch.isdigit())
NIHARIKA_ADMIN_TOKEN = os.environ.get("NIHARIKA_ADMIN_TOKEN") or os.environ.get("PICKWISE_ADMIN_TOKEN") or secrets.token_urlsafe(32)
GOOGLE_SHEETS_WEBHOOK_URL = os.environ.get("GOOGLE_SHEETS_WEBHOOK_URL", "")
GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID", "")
NIHARIKA_GEMINI_MODEL = os.environ.get("NIHARIKA_GEMINI_MODEL", "gemini-2.5-flash")
NIHARIKA_WHATSAPP_NUMBER = "".join(ch for ch in os.environ.get("NIHARIKA_WHATSAPP_NUMBER", "") if ch.isdigit())
NINA_CHAT_URL = os.environ.get("NINA_CHAT_URL", "http://127.0.0.1:5000/api/chat")
NINA_CHAT_TIMEOUT = float(os.environ.get("NINA_CHAT_TIMEOUT", "4"))
NIHARIKA_INSTAGRAM_URL = "https://www.instagram.com/direct/inbox/"
NIHARIKA_WHATSAPP_URL = "https://wa.me/918149869054"


FALLBACK_COURSERA_POSTS = [
    {
        "title": "Algorithms, AI, and better learning choices",
        "link": "https://www.coursera.org/courses?query=algorithms",
        "summary": "Explore algorithm courses and learning paths from Coursera while the live feed is unavailable.",
        "published": "Curated fallback",
    },
    {
        "title": "Computer science foundations",
        "link": "https://www.coursera.org/browse/computer-science",
        "summary": "A practical route into data structures, algorithms, programming, and software engineering.",
        "published": "Curated fallback",
    },
    {
        "title": "AI and machine learning learning paths",
        "link": "https://www.coursera.org/courses?query=machine%20learning",
        "summary": "Use Nina to compare wholesale needs before committing to the next buying step.",
        "published": "Curated fallback",
    },
]


EDTECH_APIS = [
    {
        "name": "Coursera",
        "type": "Enterprise / partner API",
        "use": "Course catalog, learner progress, enterprise learning paths, and xAPI events.",
        "status": "Configured for feed now; API keys needed for Business/Campus data.",
        "link": "https://dev.coursera.com/get-started",
    },
    {
        "name": "Udemy",
        "type": "Affiliate marketplace API",
        "use": "Course search, course listings, topic pages, and affiliate course recommendations.",
        "status": "Ready for client id, client secret, and affiliate tracking.",
        "link": "https://www.udemy.com/developers/affiliate/",
    },
    {
        "name": "edX",
        "type": "Course catalog API",
        "use": "University-style course metadata, subjects, programs, and learning catalog comparison.",
        "status": "Ready for catalog API access and token configuration.",
        "link": "https://course-catalog-api-guide.readthedocs.io/en/latest/",
    },
    {
        "name": "Canvas LMS",
        "type": "Institution LMS API",
        "use": "Courses, assignments, grades, enrollments, and school dashboard integrations.",
        "status": "Ready for OAuth token and institution Canvas URL.",
        "link": "https://canvas.instructure.com/doc/api/",
    },
    {
        "name": "Moodle",
        "type": "Open-source LMS web services",
        "use": "Course, user, enrollment, and completion data from a Moodle installation.",
        "status": "Ready for Moodle web-service token and site URL.",
        "link": "https://docs.moodle.org/dev/Web_services",
    },
    {
        "name": "Google Classroom",
        "type": "Workspace for Education API",
        "use": "Classes, rosters, coursework, submissions, and teacher/student workflows.",
        "status": "Ready for Google OAuth consent and Classroom scopes.",
        "link": "https://developers.google.com/workspace/classroom/reference/rest",
    },
    {
        "name": "xAPI",
        "type": "Learning analytics standard",
        "use": "Track learning events like started, completed, scored, watched, and practiced.",
        "status": "Ready for an LRS endpoint and credentials.",
        "link": "https://adlnet.gov/projects/xapi/",
    },
    {
        "name": "LTI 1.3",
        "type": "LMS tool integration standard",
        "use": "Launch Nina as a wholesale enquiry and recommendation tool.",
        "status": "Ready for platform registration and signing keys.",
        "link": "https://www.imsglobal.org/spec/lti/v1p3",
    },
]


TOPMATE_MENTORS = [
    {
        "name": "Gaurav Khurana",
        "focus": "QA, SDET, automation, AI testing, API testing",
        "experience": "15+ years",
        "rating": "4.9/5 public Topmate rating",
        "link": "https://topmate.io/gauravkhurana",
        "source_note": "Public Topmate profile states 15+ years in QA and automation.",
    },
    {
        "name": "Pranay Kumar Chaudhary",
        "focus": "System design, DSA, senior software engineering",
        "experience": "10+ years",
        "rating": "4.9/5 public Topmate rating",
        "link": "https://topmate.io/pranay_chaudhary",
        "source_note": "Public Topmate profile states 10+ experience.",
    },
    {
        "name": "Gaurav Singh",
        "focus": "Engineering productivity, automation, AI, interviews",
        "experience": "14+ years",
        "rating": "5/5 public Topmate rating",
        "link": "https://topmate.io/automationhacks",
        "source_note": "Public Topmate profile states 14+ years of testing industry experience.",
    },
    {
        "name": "Rapti Gupta",
        "focus": "GTM, marketing careers, founder coaching",
        "experience": "14+ years",
        "rating": "5/5 public Topmate rating",
        "link": "https://topmate.io/rapti",
        "source_note": "Public Topmate profile states 14+ years in content marketing, brand, and GTM.",
    },
    {
        "name": "Vikas Sharma",
        "focus": "Agile, Scrum, program management, TPM",
        "experience": "12+ years",
        "rating": "Listed in Topmate engineering mentors",
        "link": "https://topmate.io/vikas",
        "source_note": "Topmate engineering mentors page lists 12+ years of program management experience.",
    },
]


DEFAULT_LICENSES = {
    "48ede962654bda1040cbd345ef7ea0c0d14f7b510f9bebc22851e8a51ced1f02": {
        "customer": "Demo Customer",
        "plan": "starter",
        "status": "active",
        "expires_at": "2026-12-31",
        "features": ["license.verify", "recommend.rank", "mentor.match"],
    }
}


STYLE = """
  :root {
    color-scheme: light;
    --ink: #17191f;
    --muted: #626b76;
    --line: #dde3e8;
    --paper: #ffffff;
    --wash: #f6f8f6;
    --forest: #255245;
    --copper: #b35f38;
    --sun: #d9a441;
    --berry: #7d4d8b;
    --sky: #397c9d;
  }

  * { box-sizing: border-box; }
  html { scroll-behavior: smooth; }

  body {
    margin: 0;
    font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    color: var(--ink);
    background: var(--wash);
    line-height: 1.5;
  }

  a { color: inherit; text-decoration: none; }

  .topbar {
    position: sticky;
    top: 0;
    z-index: 20;
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 18px;
    padding: 14px clamp(18px, 5vw, 64px);
    background: rgba(255, 255, 255, 0.94);
    border-bottom: 1px solid var(--line);
    backdrop-filter: blur(12px);
  }

  .brand {
    display: flex;
    align-items: center;
    gap: 10px;
    min-width: 0;
    font-weight: 900;
    letter-spacing: 0;
  }

  .mark {
    display: grid;
    width: 36px;
    height: 36px;
    place-items: center;
    border-radius: 8px;
    background: var(--forest);
    color: white;
    font-weight: 900;
  }

  nav {
    display: flex;
    gap: clamp(10px, 2vw, 24px);
    color: var(--muted);
    font-size: 0.94rem;
    white-space: nowrap;
  }

  .hero {
    display: grid;
    grid-template-columns: minmax(0, 1fr) minmax(280px, 0.92fr);
    gap: clamp(28px, 5vw, 68px);
    align-items: center;
    min-height: min(690px, calc(100vh - 64px));
    padding: clamp(42px, 7vw, 88px) clamp(18px, 5vw, 64px) 38px;
    background:
      linear-gradient(115deg, rgba(37, 82, 69, 0.13), rgba(217, 164, 65, 0.12), rgba(57, 124, 157, 0.1)),
      var(--paper);
    border-bottom: 1px solid var(--line);
  }

  .eyebrow {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    margin-bottom: 18px;
    color: var(--forest);
    font-size: 0.9rem;
    font-weight: 800;
  }

  .eyebrow::before {
    content: "";
    width: 10px;
    height: 10px;
    border-radius: 999px;
    background: var(--sun);
  }

  h1 {
    max-width: 790px;
    margin: 0;
    font-size: clamp(2.65rem, 7vw, 6.2rem);
    line-height: 0.94;
    letter-spacing: 0;
  }

  .hero p {
    max-width: 650px;
    margin: 22px 0 0;
    color: var(--muted);
    font-size: clamp(1rem, 2vw, 1.23rem);
  }

  .actions {
    display: flex;
    flex-wrap: wrap;
    gap: 12px;
    margin-top: 30px;
  }

  .button {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    min-height: 44px;
    padding: 0 18px;
    border: 1px solid var(--ink);
    border-radius: 8px;
    background: var(--ink);
    color: white;
    font-weight: 800;
  }

  .button.secondary {
    background: transparent;
    color: var(--ink);
  }

  .visual {
    display: grid;
    align-items: end;
    min-height: 430px;
    overflow: hidden;
    border: 1px solid var(--line);
    border-radius: 8px;
    background:
      linear-gradient(rgba(23, 25, 31, 0.15), rgba(23, 25, 31, 0.45)),
      url("https://images.unsplash.com/photo-1516321318423-f06f85e504b3?auto=format&fit=crop&w=1200&q=80") center/cover;
    box-shadow: 0 22px 60px rgba(23, 25, 31, 0.16);
  }

  .visual-panel {
    margin: 18px;
    padding: 16px;
    border-radius: 8px;
    background: rgba(255, 255, 255, 0.92);
    border: 1px solid rgba(255, 255, 255, 0.7);
  }

  .score {
    display: flex;
    justify-content: space-between;
    gap: 16px;
    color: var(--muted);
    font-size: 0.9rem;
  }

  .score strong {
    display: block;
    color: var(--ink);
    font-size: 1.4rem;
  }

  main { padding: 38px clamp(18px, 5vw, 64px) 68px; }

  .section-head {
    display: flex;
    align-items: end;
    justify-content: space-between;
    gap: 22px;
    margin: 0 0 18px;
  }

  h2 {
    margin: 0;
    font-size: clamp(1.55rem, 3vw, 2.5rem);
    letter-spacing: 0;
  }

  .section-head p {
    max-width: 560px;
    margin: 0;
    color: var(--muted);
  }

  .grid {
    display: grid;
    grid-template-columns: repeat(3, minmax(0, 1fr));
    gap: 16px;
  }

  .two-grid {
    display: grid;
    grid-template-columns: minmax(0, 0.9fr) minmax(0, 1.1fr);
    gap: 16px;
    align-items: start;
  }

  .card {
    min-height: 238px;
    padding: 20px;
    border: 1px solid var(--line);
    border-radius: 8px;
    background: var(--paper);
  }

  .compact-card { min-height: 150px; }

  .tag {
    display: inline-flex;
    margin-bottom: 28px;
    padding: 6px 9px;
    border-radius: 999px;
    color: white;
    font-size: 0.78rem;
    font-weight: 900;
  }

  .forest { background: var(--forest); }
  .copper { background: var(--copper); }
  .berry { background: var(--berry); }
  .sky { background: var(--sky); }

  .card h3 {
    margin: 0 0 10px;
    font-size: 1.18rem;
  }

  .card p {
    margin: 0;
    color: var(--muted);
  }

  .steps {
    display: grid;
    grid-template-columns: repeat(4, minmax(0, 1fr));
    gap: 1px;
    margin-top: 34px;
    overflow: hidden;
    border: 1px solid var(--line);
    border-radius: 8px;
    background: var(--line);
  }

  .step {
    padding: 18px;
    background: var(--paper);
  }

  .step strong {
    display: block;
    margin-bottom: 8px;
    color: var(--forest);
    font-size: 1.55rem;
  }

  .step span {
    color: var(--muted);
    font-size: 0.94rem;
  }

  .code-band {
    margin: 34px 0 0;
    padding: 22px;
    border-radius: 8px;
    background: #111820;
    color: #eaf1f0;
    overflow-x: auto;
  }

  .code-band pre { margin: 0; white-space: pre-wrap; }

  footer {
    display: flex;
    justify-content: space-between;
    gap: 18px;
    padding: 24px clamp(18px, 5vw, 64px);
    color: var(--muted);
    border-top: 1px solid var(--line);
    background: var(--paper);
  }

  @media (max-width: 840px) {
    .topbar, footer { align-items: flex-start; flex-direction: column; }
    nav { width: 100%; overflow-x: auto; padding-bottom: 2px; }
    .hero, .grid, .two-grid, .steps { grid-template-columns: 1fr; }
    .hero { min-height: auto; }
    .visual { min-height: 310px; }
    .section-head { align-items: start; flex-direction: column; }
  }
"""


def page_shell(title, body, description):
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{title}</title>
  <meta name="description" content="{description}">
  <link rel="canonical" href="https://www.niharika.com/">
  <meta property="og:title" content="{title}">
  <meta property="og:description" content="{description}">
  <meta property="og:url" content="https://www.niharika.com/">
  <meta property="og:type" content="website">
  <style>{STYLE}</style>
</head>
<body>
  <header class="topbar">
    <a class="brand" href="/">
      <span class="mark">P</span>
      <span>Niharika Wholesale</span>
    </a>
    <nav aria-label="Main navigation">
      <a href="/">Home</a>
      <a href="/algorithms">Algorithms</a>
      <a href="/edtech-apis">EdTech APIs</a>
      <a href="/mentors">Mentors</a>
      <a href="#contact">Contact</a>
    </nav>
  </header>
  {body}
  <footer id="contact">
    <span>Niharika Wholesale / Nina</span>
    <span>Public website: https://www.niharika.com</span>
  </footer>
</body>
</html>
"""


HOME_HTML = page_shell(
    "Niharika Wholesale",
    """
  <section class="hero">
    <div>
      <span class="eyebrow">Sharper choices, calmer decisions</span>
      <h1>Niharika Wholesale</h1>
      <p>
        A decision guide for comparing products, tools, services, and everyday options
        with clear scoring, practical notes, and human-friendly recommendations.
      </p>
      <div class="actions">
        <a class="button" href="/algorithms">Explore algorithms</a>
        <a class="button secondary" href="#method">See method</a>
      </div>
    </div>
    <div class="visual" role="img" aria-label="Laptop showing research and selection work">
      <div class="visual-panel">
        <div class="score">
          <span><strong>94</strong>Fit score</span>
          <span><strong>12</strong>Factors checked</span>
          <span><strong>3</strong>Best picks</span>
        </div>
      </div>
    </div>
  </section>

  <main>
    <section id="picks" aria-labelledby="picks-title">
      <div class="section-head">
        <h2 id="picks-title">What Nina Can Cover</h2>
        <p>Balanced recommendation pages for people who want clarity before spending time or money.</p>
      </div>
      <div class="grid">
        <article class="card">
          <span class="tag forest">Tech</span>
          <h3>Gadgets and Tools</h3>
          <p>Compare phones, laptops, apps, AI tools, and web services by price, features, and real usefulness.</p>
        </article>
        <article class="card">
          <span class="tag copper">Lifestyle</span>
          <h3>Daily Decisions</h3>
          <p>Turn confusing choices into simple shortlists for travel, shopping, study plans, and home upgrades.</p>
        </article>
        <article class="card">
          <span class="tag berry">Learning</span>
          <h3>Course Selection</h3>
          <p>Use learning goals, budget, difficulty, and outcomes to pick stronger courses and paths.</p>
        </article>
      </div>
    </section>

    <section id="method" class="steps" aria-label="Niharika wholesale method">
      <div class="step"><strong>01</strong><span>Collect options and key details.</span></div>
      <div class="step"><strong>02</strong><span>Compare features, price, risks, and support.</span></div>
      <div class="step"><strong>03</strong><span>Score each option against the user's goal.</span></div>
      <div class="step"><strong>04</strong><span>Recommend the best pick with clear reasons.</span></div>
    </section>
  </main>
""",
    "Niharika Wholesale helps buyers share requirements and get clearer next steps with Nina.",
)


def fetch_coursera_posts(limit=3):
    request = Request(COURSERA_BLOG_FEED, headers={"User-Agent": "niharika-wholesale/1.0"})
    with urlopen(request, timeout=6) as response:
        feed_xml = response.read()

    root = ET.fromstring(feed_xml)
    items = root.findall(".//item")
    posts = []
    for item in items[:limit]:
        title = item.findtext("title", default="Coursera update").strip()
        link = item.findtext("link", default="https://blog.coursera.org/").strip()
        summary = item.findtext("description", default="Latest Coursera learning insight.").strip()
        published = item.findtext("pubDate", default="Latest").strip()
        posts.append(
            {
                "title": title,
                "link": link,
                "summary": summary,
                "published": published,
            }
        )
    return posts or FALLBACK_COURSERA_POSTS


def get_coursera_posts():
    try:
        return fetch_coursera_posts()
    except Exception:
        return FALLBACK_COURSERA_POSTS


def post_cards(posts):
    cards = []
    for post in posts:
        cards.append(
            f"""
        <article class="card compact-card">
          <span class="tag sky">Coursera</span>
          <h3><a href="{escape(post['link'])}" target="_blank" rel="noopener">{escape(post['title'])}</a></h3>
          <p>{escape(strip_html(post['summary'])[:180])}</p>
          <p style="margin-top: 12px; font-size: 0.88rem;">{escape(post['published'])}</p>
        </article>"""
        )
    return "\n".join(cards)


def api_cards(apis):
    cards = []
    for api in apis:
        cards.append(
            f"""
        <article class="card">
          <span class="tag sky">{escape(api['type'])}</span>
          <h3>{escape(api['name'])}</h3>
          <p>{escape(api['use'])}</p>
          <p style="margin-top: 12px;"><strong>Status:</strong> {escape(api['status'])}</p>
          <p style="margin-top: 14px;"><a class="button secondary" href="{escape(api['link'])}" target="_blank" rel="noopener">Docs</a></p>
        </article>"""
        )
    return "\n".join(cards)


def mentor_cards(mentors):
    cards = []
    for mentor in mentors:
        cards.append(
            f"""
        <article class="card">
          <span class="tag forest">{escape(mentor['experience'])}</span>
          <h3>{escape(mentor['name'])}</h3>
          <p>{escape(mentor['focus'])}</p>
          <p style="margin-top: 12px;"><strong>{escape(mentor['rating'])}</strong></p>
          <p style="margin-top: 12px;">{escape(mentor['source_note'])}</p>
          <p style="margin-top: 14px;"><a class="button" href="{escape(mentor['link'])}" target="_blank" rel="noopener">Connect on Topmate</a></p>
        </article>"""
        )
    return "\n".join(cards)


def strip_html(value):
    inside = False
    output = []
    for char in value:
        if char == "<":
            inside = True
        elif char == ">":
            inside = False
        elif not inside:
            output.append(char)
    return " ".join("".join(output).split())


def license_hash(license_key):
    return hashlib.sha256(license_key.strip().encode("utf-8")).hexdigest()


def load_licenses():
    license_path = os.path.join(os.path.dirname(__file__), "licenses.json")
    if not os.path.exists(license_path):
        return DEFAULT_LICENSES

    with open(license_path, "r", encoding="utf-8-sig") as license_file:
        return json.load(license_file)


def save_licenses(licenses):
    license_path = os.path.join(os.path.dirname(__file__), "licenses.json")
    with open(license_path, "w", encoding="utf-8") as license_file:
        json.dump(licenses, license_file, indent=2)


def business_store_path():
    return os.path.join(os.path.dirname(__file__), "businesses.json")


def leads_store_path():
    return os.path.join(os.path.dirname(__file__), "leads.json")


def survey_store_path():
    return os.path.join(os.path.dirname(__file__), "survey_responses.json")


def survey_csv_path():
    return os.path.join(os.path.dirname(__file__), "survey_responses.csv")


def catalog_path():
    return os.path.join(os.path.dirname(__file__), "catalog.json")


def catalog_images_dir():
    return os.path.join(os.path.dirname(__file__), "catalog-images")


def media_dir():
    return os.path.join(os.path.dirname(__file__), "media")


def loom_media_dir():
    return os.path.join(media_dir(), "from-our-loom")


def short_film_photos_dir():
    return os.path.join(media_dir(), "short-film-photos")


def list_media_folder(folder_path, url_prefix):
    allowed_extensions = {".jpg", ".jpeg", ".png", ".webp", ".mp4", ".mov", ".m4v", ".webm"}
    if not os.path.isdir(folder_path):
        return []

    items = []
    for filename in sorted(os.listdir(folder_path)):
        extension = os.path.splitext(filename)[1].lower()
        if extension not in allowed_extensions:
            continue
        media_type = "video" if extension in {".mp4", ".mov", ".m4v", ".webm"} else "image"
        items.append(
            {
                "name": filename,
                "type": media_type,
                "url": f"{url_prefix}/{filename}",
            }
        )
    return items


def list_loom_media():
    return list_media_folder(loom_media_dir(), "/media/from-our-loom")


def list_short_film_media():
    return list_media_folder(short_film_photos_dir(), "/media/short-film-photos")


def customer_store_path():
    return os.path.join(os.path.dirname(__file__), "customers.json")


def load_businesses():
    path = business_store_path()
    if not os.path.exists(path):
        return {}
    with open(path, "r", encoding="utf-8-sig") as business_file:
        return json.load(business_file)


def save_businesses(businesses):
    with open(business_store_path(), "w", encoding="utf-8") as business_file:
        json.dump(businesses, business_file, indent=2)


def load_leads():
    path = leads_store_path()
    if not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf-8-sig") as leads_file:
        return json.load(leads_file)


def save_leads(leads):
    with open(leads_store_path(), "w", encoding="utf-8") as leads_file:
        json.dump(leads, leads_file, indent=2)


def load_survey_responses():
    path = survey_store_path()
    if not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf-8-sig") as survey_file:
        return json.load(survey_file)


def save_survey_responses(responses):
    with open(survey_store_path(), "w", encoding="utf-8") as survey_file:
        json.dump(responses, survey_file, indent=2)


def default_catalog():
    return [
        {
            "id": "saree-premium-001",
            "name": "Premium Saree Collection",
            "category": "Sarees",
            "description": "Wholesale saree enquiries for boutiques, resellers, and shop owners.",
            "minimum_quantity": "25 pieces",
            "price_note": "Quote after fabric, color, and quantity confirmation",
            "image_url": "",
            "instagram_url": NIHARIKA_INSTAGRAM_URL,
        },
        {
            "id": "kurti-wholesale-001",
            "name": "Kurti Wholesale Set",
            "category": "Kurtis",
            "description": "Kurti catalogue option for store inventory and boutique buying.",
            "minimum_quantity": "30 pieces",
            "price_note": "Opening sale: Kurtis at Rs. 1500",
            "image_url": "",
            "instagram_url": NIHARIKA_INSTAGRAM_URL,
        },
        {
            "id": "crop-top-001",
            "name": "Crop Top Collection",
            "category": "Crop tops",
            "description": "Crop top wholesale enquiries with quantity, color, and size requirements.",
            "minimum_quantity": "30 pieces",
            "price_note": "Quote after quantity and size details",
            "image_url": "",
            "instagram_url": NIHARIKA_INSTAGRAM_URL,
        },
    ]


def load_catalog():
    path = catalog_path()
    if not os.path.exists(path):
        return default_catalog()
    try:
        with open(path, "r", encoding="utf-8") as catalog_file:
            catalog = json.load(catalog_file)
        if isinstance(catalog, list):
            return catalog
    except (json.JSONDecodeError, OSError):
        pass
    return default_catalog()


def load_customers():
    path = customer_store_path()
    if not os.path.exists(path):
        return {}
    with open(path, "r", encoding="utf-8") as customer_file:
        return json.load(customer_file)


def save_customers(customers):
    with open(customer_store_path(), "w", encoding="utf-8") as customer_file:
        json.dump(customers, customer_file, indent=2)


def public_customer_record(customer):
    return {
        "email": customer.get("email"),
        "name": customer.get("name"),
        "picture": customer.get("picture"),
        "provider": customer.get("provider"),
        "last_login_at": customer.get("last_login_at"),
    }


def verify_google_id_token(id_token):
    if not GOOGLE_CLIENT_ID:
        return None, "GOOGLE_CLIENT_ID is not configured."
    if not id_token:
        return None, "Google credential is required."

    tokeninfo_url = "https://oauth2.googleapis.com/tokeninfo?id_token=" + quote_plus(id_token)
    try:
        with urlopen(tokeninfo_url, timeout=8) as response:
            claims = json.loads(response.read().decode("utf-8"))
    except (HTTPError, URLError, TimeoutError, json.JSONDecodeError) as error:
        return None, f"Could not verify Google token: {error}"

    if claims.get("aud") != GOOGLE_CLIENT_ID:
        return None, "Google token audience does not match this app."
    if claims.get("email_verified") not in {"true", True}:
        return None, "Google email is not verified."

    return claims, None


def sign_in_customer_with_google(payload):
    claims, error = verify_google_id_token(payload.get("credential"))
    if error:
        return None, error

    email = normalize_email(claims.get("email"))
    customers = load_customers()
    customer = customers.get(email, {})
    customer.update(
        {
            "email": email,
            "name": claims.get("name", ""),
            "picture": claims.get("picture", ""),
            "provider": "google",
            "google_sub": claims.get("sub"),
            "last_login_at": datetime.now(timezone.utc).isoformat(),
        }
    )
    customers[email] = customer
    save_customers(customers)
    return customer, None


def append_survey_csv(response):
    path = survey_csv_path()
    fieldnames = [
        "id",
        "created_at",
        "wholesale_order_no",
        "name",
        "email",
        "phone",
        "business_name",
        "instagram_handle",
        "buyer_type",
        "product_category",
        "pieces_required",
        "budget",
        "delivery_city",
        "timeline",
        "requirements",
        "source",
    ]
    file_exists = os.path.exists(path)
    with open(path, "a", encoding="utf-8", newline="") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        if not file_exists:
            writer.writeheader()
        writer.writerow({field: response.get(field, "") for field in fieldnames})


def survey_csv_content():
    fieldnames = [
        "id",
        "created_at",
        "wholesale_order_no",
        "name",
        "email",
        "phone",
        "business_name",
        "instagram_handle",
        "buyer_type",
        "product_category",
        "pieces_required",
        "budget",
        "delivery_city",
        "timeline",
        "requirements",
        "source",
    ]
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=fieldnames)
    writer.writeheader()
    for response in load_survey_responses():
        writer.writerow({field: response.get(field, "") for field in fieldnames})
    return output.getvalue()


def post_to_google_sheets(response):
    if not GOOGLE_SHEETS_WEBHOOK_URL:
        return {"enabled": False, "sent": False}

    request = Request(
        GOOGLE_SHEETS_WEBHOOK_URL,
        data=json.dumps(response).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urlopen(request, timeout=8) as sheet_response:
            return {
                "enabled": True,
                "sent": 200 <= sheet_response.status < 300,
                "status": sheet_response.status,
            }
    except (HTTPError, URLError, TimeoutError) as error:
        return {"enabled": True, "sent": False, "error": str(error)}


def survey_whatsapp_message(response):
    lines = [
        "New Niharika wholesale requirement",
        f"Reference: {response.get('id', '')}",
        f"Order no: {response.get('wholesale_order_no', '')}",
        f"Name: {response.get('name', '')}",
        f"Phone: {response.get('phone', '')}",
        f"Business: {response.get('business_name', '')}",
        f"Instagram: @{response.get('instagram_handle', '')}" if response.get("instagram_handle") else "",
        f"Buyer type: {response.get('buyer_type', '')}",
        f"Category: {response.get('product_category', '')}",
        f"Pieces: {response.get('pieces_required', '')}",
        f"Budget: {response.get('budget', '')}" if response.get("budget") else "",
        f"Delivery city: {response.get('delivery_city', '')}",
        f"Timeline: {response.get('timeline', '')}" if response.get("timeline") else "",
        f"Requirements: {response.get('requirements', '')}" if response.get("requirements") else "",
    ]
    return "\n".join(line for line in lines if line)


def survey_whatsapp_url(response):
    if not NIHARIKA_WHATSAPP_NUMBER:
        return ""
    return f"https://wa.me/{NIHARIKA_WHATSAPP_NUMBER}?text={quote_plus(survey_whatsapp_message(response))}"


def save_survey_response(payload):
    required = ["wholesale_order_no", "name", "phone", "business_name", "product_category", "pieces_required", "delivery_city"]
    missing = [field for field in required if not (payload.get(field) or "").strip()]
    if missing:
        return None, {"error": "Missing required fields.", "missing": missing}

    response = {
        "id": "survey_" + secrets.token_hex(8),
        "created_at": datetime.now(timezone.utc).isoformat(),
        "wholesale_order_no": (payload.get("wholesale_order_no") or "").strip(),
        "name": (payload.get("name") or "").strip(),
        "email": normalize_email(payload.get("email")),
        "phone": (payload.get("phone") or "").strip(),
        "business_name": (payload.get("business_name") or "").strip(),
        "instagram_handle": (payload.get("instagram_handle") or "").strip().lstrip("@"),
        "buyer_type": (payload.get("buyer_type") or "wholesale buyer").strip(),
        "product_category": (payload.get("product_category") or "").strip(),
        "pieces_required": (payload.get("pieces_required") or payload.get("quantity") or "").strip(),
        "budget": (payload.get("budget") or "").strip(),
        "delivery_city": (payload.get("delivery_city") or "").strip(),
        "timeline": (payload.get("timeline") or "").strip(),
        "requirements": (payload.get("requirements") or "").strip(),
        "source": (payload.get("source") or "niharika-survey").strip(),
    }
    responses = load_survey_responses()
    responses.insert(0, response)
    save_survey_responses(responses)
    append_survey_csv(response)
    sheet_result = post_to_google_sheets(response)
    response["google_sheets"] = sheet_result
    response["whatsapp_url"] = survey_whatsapp_url(response)
    return response, None


def save_lead(payload, nina_result):
    leads = load_leads()
    lead = {
        "id": "lead_" + secrets.token_hex(8),
        "created_at": datetime.now(timezone.utc).isoformat(),
        "status": "new",
        "buyer_name": (payload.get("buyer_name") or "").strip(),
        "buyer_email": normalize_email(payload.get("buyer_email")),
        "buyer_phone": (payload.get("buyer_phone") or "").strip(),
        "buyer_type": (payload.get("buyer_type") or "wholesale buyer").strip(),
        "message": (payload.get("message") or "").strip(),
        "reply": nina_result.get("reply", ""),
        "next_question": nina_result.get("next_question", ""),
        "requirements": nina_result.get("requirements", {}),
    }
    leads.insert(0, lead)
    save_leads(leads)
    return lead


def update_lead_status(payload):
    lead_id = payload.get("lead_id")
    status = payload.get("status")
    allowed = {"new", "contacted", "converted", "closed"}
    if status not in allowed:
        return None, "Invalid lead status."

    leads = load_leads()
    for lead in leads:
        if lead.get("id") == lead_id:
            lead["status"] = status
            lead["updated_at"] = datetime.now(timezone.utc).isoformat()
            save_leads(leads)
            return lead, None
    return None, "Lead not found."


def normalize_email(email):
    return (email or "").strip().lower()


def password_hash(password, salt=None):
    salt = salt or secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt.encode("utf-8"), 120000)
    return salt, digest.hex()


def verify_password(password, salt, digest):
    _, check = password_hash(password, salt)
    return secrets.compare_digest(check, digest)


def make_customer_license():
    return "PW-" + secrets.token_urlsafe(18).replace("-", "").replace("_", "")[:22].upper()


def get_business_by_license_hash(license_key_hash):
    for business in load_businesses().values():
        if business.get("license_hash") == license_key_hash:
            return business
    return None


def get_license_record(license_key):
    if not license_key:
        return None
    return load_licenses().get(license_hash(license_key))


def is_license_active(record):
    if not record or record.get("status") != "active":
        return False

    expires_at = record.get("expires_at")
    if not expires_at:
        return True

    expiry = datetime.fromisoformat(expires_at).date()
    if expiry < datetime.now(timezone.utc).date():
        return False

    business = get_business_by_license_hash(record.get("license_hash", ""))
    if not business:
        return True

    return business.get("payment_status") == "active" and business.get("instagram_status") == "verified"


def public_license_record(record):
    if not record:
        return None
    return {
        "customer": record.get("customer"),
        "plan": record.get("plan"),
        "status": record.get("status"),
        "expires_at": record.get("expires_at"),
        "features": record.get("features", []),
    }


def public_business_record(business):
    return {
        "business_name": business.get("business_name"),
        "email": business.get("email"),
        "instagram_handle": business.get("instagram_handle"),
        "website": business.get("website"),
        "shopify_store_domain": business.get("shopify_store_domain"),
        "shopify_status": business.get("shopify_status", "not_connected"),
        "payment_status": business.get("payment_status"),
        "instagram_status": business.get("instagram_status"),
        "plan": business.get("plan"),
        "price_inr": business.get("price_inr"),
        "license_key": business.get("license_key"),
    }


def payment_link_for_business(business):
    if RAZORPAY_SUBSCRIPTION_LINK:
        separator = "&" if "?" in RAZORPAY_SUBSCRIPTION_LINK else "?"
        return (
            f"{RAZORPAY_SUBSCRIPTION_LINK}{separator}"
            f"customer_email={quote_plus(business.get('email', ''))}"
            f"&reference_id={quote_plus(business.get('license_key', ''))}"
        )

    if BHIM_UPI_ID:
        note = quote_plus(f"Niharika monthly business access {business.get('business_name', '')}")
        return f"upi://pay?pa={quote_plus(BHIM_UPI_ID)}&pn=Niharika&am={MONTHLY_PRICE_INR}&cu=INR&tn={note}"

    return ""


def payment_instruction_for_business():
    if BHIM_UPI_ID:
        return f"UPI receiver: {BHIM_UPI_ID}"
    if NIHARIKA_PAYMENT_PHONE:
        return f"UPI receiver phone: {NIHARIKA_PAYMENT_PHONE}. Add the exact UPI ID in NIHARIKA_UPI_ID to enable one-tap UPI payment."
    return "Set NIHARIKA_UPI_ID to enable one-tap UPI payment."


def payment_whatsapp_url(business):
    if not NIHARIKA_WHATSAPP_NUMBER:
        return ""
    lines = [
        "Niharika payment confirmation",
        f"Business: {business.get('business_name', '')}",
        f"Email: {business.get('email', '')}",
        f"Instagram: @{business.get('instagram_handle', '')}",
        f"Plan: First month free, then Rs. {MONTHLY_PRICE_INR}/month",
        f"License: {business.get('license_key', '')}",
        payment_instruction_for_business(),
    ]
    return f"https://wa.me/{NIHARIKA_WHATSAPP_NUMBER}?text={quote_plus(chr(10).join(lines))}"


def create_business(payload):
    email = normalize_email(payload.get("email"))
    password = payload.get("password", "")
    business_name = (payload.get("business_name") or "").strip()
    instagram_handle = (payload.get("instagram_handle") or "").strip().lstrip("@")

    if not email or not password or not business_name or not instagram_handle:
        return None, "business_name, email, password, and instagram_handle are required."

    businesses = load_businesses()
    if email in businesses:
        return None, "Business already exists. Please sign in."

    license_key = make_customer_license()
    key_hash = license_hash(license_key)
    salt, digest = password_hash(password)
    now = datetime.now(timezone.utc).isoformat()

    business = {
        "business_name": business_name,
        "email": email,
        "password_salt": salt,
        "password_hash": digest,
        "instagram_handle": instagram_handle,
        "website": (payload.get("website") or "").strip(),
        "shopify_store_domain": normalize_shopify_domain(payload.get("shopify_store_domain")),
        "shopify_status": "pending" if payload.get("shopify_store_domain") else "not_connected",
        "payment_status": "trial",
        "instagram_status": "pending",
        "plan": "starter_trial",
        "price_inr": MONTHLY_PRICE_INR,
        "license_key": license_key,
        "license_hash": key_hash,
        "created_at": now,
        "updated_at": now,
    }
    businesses[email] = business
    save_businesses(businesses)

    licenses = load_licenses()
    licenses[key_hash] = {
        "customer": business_name,
        "plan": "starter",
        "status": "active",
        "expires_at": "2026-12-31",
        "features": ["license.verify", "recommend.rank", "mentor.match"],
        "license_hash": key_hash,
    }
    save_licenses(licenses)
    return business, None


def normalize_shopify_domain(value):
    domain = (value or "").strip().lower()
    domain = domain.replace("https://", "").replace("http://", "").strip("/")
    if domain and "." not in domain:
        domain = f"{domain}.myshopify.com"
    return domain


def shopify_product_url(store_domain, option):
    store = normalize_shopify_domain(store_domain)
    if not store:
        return ""

    direct_url = (option.get("product_url") or option.get("shopify_url") or "").strip()
    if direct_url.startswith("http://") or direct_url.startswith("https://"):
        return direct_url

    handle = (option.get("product_handle") or option.get("handle") or "").strip().strip("/")
    if handle:
        return f"https://{store}/products/{quote_plus(handle).replace('%2F', '/')}"

    search = quote_plus(option.get("name", ""))
    return f"https://{store}/search?q={search}"


def connect_shopify_store(payload):
    email = normalize_email(payload.get("email"))
    businesses = load_businesses()
    business = businesses.get(email)
    if not business:
        return None, "Business not found."

    if payload.get("license_key") != business.get("license_key"):
        return None, "Valid business license key required."

    store_domain = normalize_shopify_domain(payload.get("shopify_store_domain"))
    if not store_domain:
        return None, "shopify_store_domain is required."

    business["shopify_store_domain"] = store_domain
    business["shopify_status"] = "connected_public_links"
    if payload.get("shopify_admin_access_token"):
        business["shopify_status"] = "token_saved_local"
        business["shopify_admin_access_token"] = payload["shopify_admin_access_token"]
    business["updated_at"] = datetime.now(timezone.utc).isoformat()
    businesses[email] = business
    save_businesses(businesses)
    return business, None


def get_business_by_license_key(license_key):
    key_hash = license_hash(license_key)
    return get_business_by_license_hash(key_hash)


def sign_in_business(payload):
    email = normalize_email(payload.get("email"))
    password = payload.get("password", "")
    business = load_businesses().get(email)
    if not business or not verify_password(password, business["password_salt"], business["password_hash"]):
        return None
    return business


def admin_update_business(payload):
    if payload.get("admin_token") != NIHARIKA_ADMIN_TOKEN:
        return None, "Invalid admin token."

    email = normalize_email(payload.get("email"))
    businesses = load_businesses()
    business = businesses.get(email)
    if not business:
        return None, "Business not found."

    if payload.get("payment_status"):
        business["payment_status"] = payload["payment_status"]
    if payload.get("instagram_status"):
        business["instagram_status"] = payload["instagram_status"]
    business["updated_at"] = datetime.now(timezone.utc).isoformat()
    businesses[email] = business
    save_businesses(businesses)
    return business, None


def extract_license_key(headers, payload):
    auth = headers.get("Authorization", "")
    if auth.lower().startswith("bearer "):
        return auth.split(" ", 1)[1].strip()
    return headers.get("X-Niharika-License") or payload.get("license_key")


def score_option(option, weights):
    score = 0
    reasons = []
    for signal, weight in weights.items():
        value = float(option.get(signal, 0) or 0)
        score += value * float(weight)
        if value >= 8:
            reasons.append(f"Strong {signal.replace('_', ' ')}")
    return round(min(score, 100), 2), reasons[:3]


def rank_recommendations(payload):
    options = payload.get("options") or []
    store_domain = payload.get("shopify_store_domain", "")
    weights = payload.get("weights") or {
        "quality": 3.0,
        "price_fit": 2.0,
        "outcome_fit": 3.0,
        "support": 2.0,
    }
    ranked = []

    for option in options:
        score, reasons = score_option(option, weights)
        ranked.append(
            {
                "name": option.get("name", "Untitled option"),
                "score": score,
                "reasons": reasons or ["Good overall fit"],
                "next_step": option.get("next_step", "Review this option with the customer."),
                "shopify_url": shopify_product_url(store_domain, option),
            }
        )

    ranked.sort(key=lambda item: item["score"], reverse=True)
    return ranked


def free_retail_wholesale_rank(payload):
    request_type = (payload.get("request_type") or payload.get("buyer_type") or "wholesale").strip().lower()
    options = payload.get("options") or load_catalog()
    weights = payload.get("weights") or {
        "category_fit": 3.0,
        "quantity_fit": 2.5,
        "budget_fit": 2.0,
        "delivery_fit": 1.5,
        "availability": 1.0,
    }
    ranked = []
    preferred_category = (payload.get("product_category") or payload.get("category") or "").strip().lower()

    for option in options:
        category = (option.get("category") or "").strip().lower()
        score_inputs = {
            "category_fit": 10 if preferred_category and preferred_category == category else 7,
            "quantity_fit": 9 if request_type in {"wholesale", "reseller", "boutique", "shop owner"} else 6,
            "budget_fit": 7,
            "delivery_fit": 7,
            "availability": 8,
        }
        score, reasons = score_option(score_inputs, weights)
        ranked.append(
            {
                "id": option.get("id"),
                "name": option.get("name", "Niharika catalogue option"),
                "category": option.get("category", ""),
                "score": score,
                "reasons": reasons or ["Good fit for buyer enquiry"],
                "minimum_quantity": option.get("minimum_quantity", ""),
                "price_note": option.get("price_note", "Quote after requirement confirmation"),
                "next_step": "Send category, quantity, budget, delivery city, and phone number.",
                "image_url": option.get("image_url", ""),
                "instagram_url": option.get("instagram_url", NIHARIKA_INSTAGRAM_URL),
            }
        )

    ranked.sort(key=lambda item: item["score"], reverse=True)
    return ranked


def free_requirement_payload(payload):
    message = (payload.get("message") or payload.get("requirements") or "").strip()
    if not message:
        message = (
            f"{payload.get('product_category', '')} "
            f"{payload.get('pieces_required', payload.get('quantity', ''))} "
            f"{payload.get('budget', '')} "
            f"{payload.get('delivery_city', '')}"
        ).strip()
    result = nina_requirement_reply({**payload, "message": message})
    lead = save_lead(
        {
            "buyer_name": payload.get("name") or payload.get("buyer_name", ""),
            "buyer_email": payload.get("email") or payload.get("buyer_email", ""),
            "buyer_phone": payload.get("phone") or payload.get("buyer_phone", ""),
            "buyer_type": payload.get("buyer_type") or payload.get("request_type") or "wholesale buyer",
            "message": message,
        },
        result,
    )
    result["lead_id"] = lead["id"]
    result["free_api"] = True
    return result


def niharika_api_chat(payload):
    message = (payload.get("message") or payload.get("requirements") or "").strip()
    if not message:
        message = (
            f"{payload.get('product_category', payload.get('category', ''))} "
            f"{payload.get('quantity', payload.get('pieces_required', ''))} "
            f"{payload.get('budget', '')} "
            f"{payload.get('delivery_city', '')}"
        ).strip()

    requirement_result = nina_requirement_reply({**payload, "message": message})
    recommendations = free_retail_wholesale_rank(payload)
    best_pick = recommendations[0] if recommendations else None

    fallback_reply = requirement_result.get("reply", "")
    api_response = {
        "free_api": True,
        "provider": "niharika",
        "model": "niharika-nina-free",
        "reply": fallback_reply,
        "requirements": requirement_result.get("requirements", {}),
        "next_question": requirement_result.get("next_question", ""),
        "recommendations": recommendations,
        "best_pick": best_pick,
        "contact": requirement_result.get("contact", {}),
    }

    if not message:
        return api_response

    if not (os.environ.get("GOOGLE_API_KEY") or os.environ.get("GEMINI_API_KEY")):
        api_response["ai_status"] = "fallback_no_google_api_key"
        return api_response

    try:
        from google import genai
        from google.genai import types

        context = {
            "brand": "Niharika Wholesale",
            "categories": ["Sarees", "Kurtis", "Crop tops"],
            "buyer_type": payload.get("buyer_type") or payload.get("request_type") or "wholesale buyer",
            "recommendation": best_pick,
            "requirements": requirement_result.get("requirements", {}),
        }
        prompt = (
            "You are Nina, the Niharika wholesale and retail buying assistant. "
            "Keep the answer under 3 sentences, avoid markdown, and end with one targeted follow-up question. "
            f"Context JSON: {json.dumps(context, ensure_ascii=True)}\n"
            f"Customer message: {message}"
        )
        client = genai.Client()
        response = client.models.generate_content(
            model=NIHARIKA_GEMINI_MODEL,
            contents=prompt,
            config=types.GenerateContentConfig(temperature=0.5),
        )
        api_response["provider"] = "google-gemini"
        api_response["model"] = NIHARIKA_GEMINI_MODEL
        api_response["reply"] = response.text or fallback_reply
        api_response["ai_status"] = "ok"
    except Exception as exc:
        api_response["ai_status"] = "fallback_gemini_error"
        api_response["ai_error"] = str(exc)

    return api_response


def call_nina_chatbot(payload):
    if not NINA_CHAT_URL:
        return None

    message = (payload.get("message") or payload.get("requirements") or "").strip()
    if not message:
        return None

    body = json.dumps(
        {
            "message": message,
            "user_type": (payload.get("buyer_type") or "wholesale buyer").strip(),
        }
    ).encode("utf-8")
    request = Request(
        NINA_CHAT_URL,
        data=body,
        headers={"Content-Type": "application/json", "Accept": "application/json"},
        method="POST",
    )

    try:
        with urlopen(request, timeout=NINA_CHAT_TIMEOUT) as response:
            return json.loads(response.read().decode("utf-8"))
    except (HTTPError, URLError, TimeoutError, OSError, json.JSONDecodeError) as exc:
        return {"error": str(exc)}


def connected_nina_requirement_reply(payload):
    result = niharika_api_chat(payload)
    chatbot_response = call_nina_chatbot(payload)

    if chatbot_response and chatbot_response.get("reply"):
        result["reply"] = chatbot_response["reply"]
        result["provider"] = "nina-chatbot"
        result["model"] = "nina.py"
        result["chatbot_status"] = "connected"
    elif chatbot_response and chatbot_response.get("error"):
        result["chatbot_status"] = "fallback_nina_unavailable"
        result["chatbot_error"] = chatbot_response["error"]
    else:
        result["chatbot_status"] = "fallback_local"

    return result


def nina_requirement_reply(payload):
    message = (payload.get("message") or "").strip()
    buyer_type = (payload.get("buyer_type") or "wholesale buyer").strip()
    lower = message.lower()

    if not message:
        return {
            "reply": "Hi, I am Nina for Niharika. Tell me what products you need, quantity, budget range, delivery city, and whether this is for resale, gifting, or store inventory.",
            "requirements": {},
            "next_question": "What product category are you looking for first?",
        }

    requirements = {
        "buyer_type": buyer_type,
        "raw_need": message,
        "detected_signals": [],
    }
    signals = {
        "bulk_quantity": ["bulk", "wholesale", "carton", "dozen", "100", "500", "1000"],
        "urgent_delivery": ["urgent", "today", "tomorrow", "fast", "quick"],
        "budget_sensitive": ["cheap", "budget", "low price", "affordable", "discount"],
        "premium_quality": ["premium", "quality", "export", "best", "branded"],
        "reseller": ["resell", "reseller", "shop", "store", "boutique"],
    }
    for signal, words in signals.items():
        if any(word in lower for word in words):
            requirements["detected_signals"].append(signal)

    if "price" in lower or "budget" in lower or "cost" in lower:
        reply = "For wholesale pricing, I need product category, approximate quantity, and delivery city. Niharika can then share the best-fit wholesale option and next buying step."
        next_question = "What quantity range should I quote for you?"
    elif "instagram" in lower or "ig" in lower:
        reply = "I can use the Instagram business handle as a trust signal and route verified businesses into Niharika business access. For wholesale buying, I still need product category and quantity."
        next_question = "Which Instagram business handle should Niharika verify?"
    elif requirements["detected_signals"]:
        reply = "I found a few buying signals from your message. To recommend correctly, Niharika needs category, quantity, budget range, delivery location, and expected purchase timeline."
        next_question = "Which delivery city and timeline should I note?"
    else:
        reply = "Thanks, I can help collect the wholesale requirement for Niharika. Please share product type, quantity, target price range, delivery city, and whether you are buying for resale or personal use."
        next_question = "What product type and quantity do you need?"

    return {
        "reply": reply,
        "requirements": requirements,
        "next_question": next_question,
        "contact": {
            "email": "sivashankarimurugesan@niharika.com",
            "whatsapp": NIHARIKA_WHATSAPP_URL,
            "instagram": NIHARIKA_INSTAGRAM_URL,
            "website": "https://niharika.com/",
        },
    }


def algorithms_html(posts=None):
    posts = posts or FALLBACK_COURSERA_POSTS
    return page_shell(
        "Niharika Wholesale",
        f"""
  <section class="hero">
    <div>
      <span class="eyebrow">Algorithmic thinking for real choices</span>
      <h1>Algorithms</h1>
      <p>
        Nina explains wholesale choices as practical decision signals: category,
        reduce noise, compare tradeoffs, and turn learning into action.
      </p>
      <div class="actions">
        <a class="button" href="#coursera">Coursera blogs</a>
        <a class="button secondary" href="#nginx">Nginx setup</a>
      </div>
    </div>
    <div class="visual" role="img" aria-label="Programming workspace with algorithm research">
      <div class="visual-panel">
        <div class="score">
          <span><strong>4</strong>Steps</span>
          <span><strong>3</strong>Signals</span>
          <span><strong>1</strong>Pick</span>
        </div>
      </div>
    </div>
  </section>

  <main>
    <section aria-labelledby="algorithm-method">
      <div class="section-head">
        <h2 id="algorithm-method">Decision Algorithms</h2>
        <p>Simple scoring models for comparing courses, products, and tools without drowning users in data.</p>
      </div>
      <div class="grid">
        <article class="card">
          <span class="tag forest">Rank</span>
          <h3>Weighted Scoring</h3>
          <p>Assign importance to price, quality, difficulty, outcomes, and support, then rank options transparently.</p>
        </article>
        <article class="card">
          <span class="tag copper">Filter</span>
          <h3>Constraint Matching</h3>
          <p>Remove options that fail must-have rules like budget, time, skill level, or delivery format.</p>
        </article>
        <article class="card">
          <span class="tag berry">Explain</span>
          <h3>Reason Codes</h3>
          <p>Show why a pick wins, where it is weak, and who should choose a different option.</p>
        </article>
      </div>
    </section>

    <section id="coursera" style="margin-top: 38px;" aria-labelledby="coursera-title">
      <div class="section-head">
        <h2 id="coursera-title">Coursera Learning Feed</h2>
        <p>The Python app fetches Coursera blog RSS when available. Static hosting shows curated fallback cards.</p>
      </div>
      <div class="grid">
        {post_cards(posts)}
      </div>
    </section>

    <section id="nginx" style="margin-top: 38px;" aria-labelledby="nginx-title">
      <div class="section-head">
        <h2 id="nginx-title">Nginx Integration</h2>
        <p>Use Nginx as the public reverse proxy when this Python app runs on a VPS.</p>
      </div>
      <div class="two-grid">
        <article class="card">
          <span class="tag sky">Proxy</span>
          <h3>Python behind Nginx</h3>
          <p>Nginx receives public HTTPS traffic for niharika.com and forwards local requests to Python on port 8080.</p>
        </article>
        <div class="code-band">
          <pre>server_name www.niharika.com niharika.com;
location / {{
  proxy_pass http://127.0.0.1:8000;
}}</pre>
        </div>
      </div>
    </section>
  </main>
""",
        "Niharika wholesale page with Nina buyer requirement guidance.",
    )


ALGORITHMS_HTML = algorithms_html(FALLBACK_COURSERA_POSTS)


def edtech_apis_html():
    return page_shell(
        "Niharika APIs",
        f"""
  <section class="hero">
    <div>
      <span class="eyebrow">API-ready learning marketplace</span>
      <h1>EdTech APIs</h1>
      <p>
        Nina can compare wholesale categories, buyer requirements, quantities, and follow-up options
        by connecting to education platforms with API keys or partner access.
      </p>
      <div class="actions">
        <a class="button" href="#api-stack">View API stack</a>
        <a class="button secondary" href="/mentors">Connect mentors</a>
      </div>
    </div>
    <div class="visual" role="img" aria-label="Education API dashboard">
      <div class="visual-panel">
        <div class="score">
          <span><strong>8</strong>APIs</span>
          <span><strong>3</strong>LMS paths</span>
          <span><strong>1</strong>Ranker</span>
        </div>
      </div>
    </div>
  </section>

  <main>
    <section id="api-stack" aria-labelledby="api-stack-title">
      <div class="section-head">
        <h2 id="api-stack-title">Integration Stack</h2>
        <p>These cards are wired into the website as the approved integration roadmap. Live calls need credentials, tokens, or partner approval.</p>
      </div>
      <div class="grid">
        {api_cards(EDTECH_APIS)}
      </div>
    </section>

    <section style="margin-top: 38px;" aria-labelledby="workflow-title">
      <div class="section-head">
        <h2 id="workflow-title">Niharika API Workflow</h2>
        <p>Normalize every platform into the same recommendation fields before scoring.</p>
      </div>
      <div class="steps">
        <div class="step"><strong>01</strong><span>Fetch courses, cohorts, or LMS records.</span></div>
        <div class="step"><strong>02</strong><span>Normalize price, time, level, skill tags, and outcomes.</span></div>
        <div class="step"><strong>03</strong><span>Score fit against learner goals and constraints.</span></div>
        <div class="step"><strong>04</strong><span>Recommend course, mentor, or pathway.</span></div>
      </div>
    </section>
  </main>
""",
        "Niharika API integration roadmap for wholesale enquiries, Shopify, surveys, and Nina chatbot access.",
    )


def mentors_html():
    selected = [mentor for mentor in TOPMATE_MENTORS if int(mentor["experience"].split("+")[0]) >= 7]
    return page_shell(
        "Connect Directly With Niharika",
        f"""
  <section class="hero">
    <div>
      <span class="eyebrow">Human guidance after course discovery</span>
      <h1>Connect Directly With Mentor</h1>
      <p>
        Curated Topmate mentors with public profiles showing more than 7 years of experience.
        Nina can pair wholesale buyer requirements with the right follow-up step.
      </p>
      <div class="actions">
        <a class="button" href="#mentor-list">View mentors</a>
        <a class="button secondary" href="/edtech-apis">API stack</a>
      </div>
    </div>
    <div class="visual" role="img" aria-label="Mentorship planning dashboard">
      <div class="visual-panel">
        <div class="score">
          <span><strong>7+</strong>Years</span>
          <span><strong>Topmate</strong>Links</span>
          <span><strong>Direct</strong>Connect</span>
        </div>
      </div>
    </div>
  </section>

  <main>
    <section id="mentor-list" aria-labelledby="mentor-list-title">
      <div class="section-head">
        <h2 id="mentor-list-title">Selected Mentors</h2>
        <p>Topmate has no confirmed official public search API, so this page uses curated public profile links and filters them by visible 7+ years experience signals.</p>
      </div>
      <div class="grid">
        {mentor_cards(selected)}
      </div>
    </section>

    <section style="margin-top: 38px;" aria-labelledby="mentor-workflow-title">
      <div class="section-head">
        <h2 id="mentor-workflow-title">Mentor Matching Logic</h2>
        <p>When live API access is available, Nina can rank wholesale options by category, quantity, budget, city, and urgency.</p>
      </div>
      <div class="steps">
        <div class="step"><strong>01</strong><span>Identify learner goal and target role.</span></div>
        <div class="step"><strong>02</strong><span>Filter mentors with 7+ years experience.</span></div>
        <div class="step"><strong>03</strong><span>Score domain fit, public rating, and session type.</span></div>
        <div class="step"><strong>04</strong><span>Send user to the direct Topmate booking page.</span></div>
      </div>
    </section>
  </main>
""",
        "Connect directly with curated Topmate mentors who publicly show more than 7 years of experience.",
    )


EDTECH_APIS_HTML = edtech_apis_html()
MENTORS_HTML = mentors_html()


SITEMAP_XML = """<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url>
    <loc>https://www.niharika.com/</loc>
    <lastmod>2026-06-10</lastmod>
    <priority>1.0</priority>
  </url>
  <url>
    <loc>https://www.niharika.com/survey</loc>
    <lastmod>2026-06-10</lastmod>
    <priority>0.9</priority>
  </url>
  <url>
    <loc>https://www.niharika.com/customer-login</loc>
    <lastmod>2026-06-10</lastmod>
    <priority>0.9</priority>
  </url>
  <url>
    <loc>https://www.niharika.com/admin</loc>
    <lastmod>2026-06-10</lastmod>
    <priority>0.9</priority>
  </url>
  <url>
    <loc>https://nina.niharika.com/</loc>
    <lastmod>2026-06-10</lastmod>
    <priority>0.8</priority>
  </url>
</urlset>
"""


def static_home_html():
    index_path = os.path.join(os.path.dirname(__file__), "index.html")
    with open(index_path, "r", encoding="utf-8") as index_file:
        return index_file.read()


SIGNUP_HTML = """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Niharika Business Sign In</title>
  <style>
    :root { color-scheme: dark; --bg:#080a09; --panel:#171b18; --ink:#f7f8f4; --muted:#aeb8af; --line:rgba(255,255,255,.12); --green:#36d06f; }
    * { box-sizing: border-box; }
    body { margin: 0; font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; color: var(--ink); background: var(--bg); }
    main { min-height: 100vh; display: grid; grid-template-columns: minmax(0, .9fr) minmax(340px, .72fr); gap: clamp(22px, 5vw, 70px); padding: clamp(24px, 6vw, 76px); align-items: center; }
    h1 { margin: 0; font-size: clamp(2.8rem, 8vw, 6rem); line-height: .94; letter-spacing: 0; }
    p { color: var(--muted); font-size: 1.05rem; max-width: 650px; }
    .price { display: inline-flex; align-items: baseline; gap: 8px; margin-top: 20px; padding: 14px 18px; border: 1px solid var(--line); border-radius: 8px; background: var(--panel); }
    .price strong { font-size: 2.4rem; color: var(--green); }
    form, .result { display: grid; gap: 12px; padding: 20px; border: 1px solid var(--line); border-radius: 8px; background: var(--panel); }
    label { display: grid; gap: 6px; color: var(--muted); font-size: .92rem; font-weight: 750; }
    input { min-height: 44px; padding: 0 12px; border: 1px solid var(--line); border-radius: 8px; background: #0f1210; color: var(--ink); font: inherit; }
    button, a.button { display: inline-flex; align-items: center; justify-content: center; min-height: 44px; padding: 0 16px; border: 0; border-radius: 999px; background: var(--green); color: #061109; font-weight: 900; text-decoration: none; cursor: pointer; }
    .secondary { background: rgba(255,255,255,.1) !important; color: var(--ink) !important; }
    code { word-break: break-all; color: var(--green); }
    .actions { display: flex; flex-wrap: wrap; gap: 10px; }
    @media (max-width: 840px) { main { grid-template-columns: 1fr; } }
  </style>
</head>
<body>
  <main>
    <section>
      <p>Verified Instagram business API access</p>
      <h1>Start with Niharika free for the first month.</h1>
      <p>Create a business account, connect Shopify, and get a licensed access key. Your first month is free, and ongoing billing starts at Rs. 500/month after the trial. Business access is enabled once your Instagram business is verified.</p>
      <div class="price"><strong>First month free</strong><span>Then Rs. 500 / month</span></div>
    </section>
    <section>
      <form id="signup-form">
        <label>Business name <input name="business_name" required placeholder="Looms Legacy"></label>
        <label>Email <input name="email" type="email" required placeholder="owner@example.com"></label>
        <label>Password <input name="password" type="password" required></label>
        <label>Instagram handle <input name="instagram_handle" required placeholder="@yourbrand"></label>
        <label>Website <input name="website" placeholder="https://yourstore.com"></label>
        <label>Shopify store domain <input name="shopify_store_domain" placeholder="yourstore.myshopify.com"></label>
        <button type="submit">Create Business Account</button>
      </form>
      <div id="result" class="result" hidden></div>
    </section>
  </main>
  <script>
    const form = document.querySelector("#signup-form");
    const result = document.querySelector("#result");
    form.addEventListener("submit", async (event) => {
      event.preventDefault();
      const payload = Object.fromEntries(new FormData(form).entries());
      const response = await fetch("/api/business/signup", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });
      const data = await response.json();
      result.hidden = false;
      if (!response.ok) {
        result.textContent = data.error || "Could not create account.";
        return;
      }
      result.innerHTML = `
        <strong>Account created.</strong>
        <span>API key:</span>
        <code>${data.business.license_key}</code>
        <span>Status: payment ${data.business.payment_status}, Instagram ${data.business.instagram_status}</span>
        <div class="actions">
          ${data.payment_link ? `<a class="button" href="${data.payment_link}">Set up payment after trial</a>` : ""}
          ${data.payment_whatsapp_url ? `<a class="button secondary" href="${data.payment_whatsapp_url}" target="_blank" rel="noopener">Send payment message</a>` : ""}
          <a class="button secondary" href="https://www.instagram.com/${data.business.instagram_handle}/" target="_blank" rel="noopener">Open Instagram</a>
        </div>
        <span>First month is free. ${data.payment_instruction || ""}</span>
      `;
    });
  </script>
</body>
</html>"""


ADMIN_HTML = """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Niharika Admin</title>
  <style>
    :root { color-scheme: dark; --bg:#080a09; --panel:#171b18; --ink:#f7f8f4; --muted:#aeb8af; --line:rgba(255,255,255,.12); --green:#36d06f; --yellow:#d9a441; }
    * { box-sizing: border-box; }
    body { margin:0; font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; color:var(--ink); background:var(--bg); }
    header, main { padding: clamp(18px, 4vw, 44px); }
    header { display:flex; align-items:end; justify-content:space-between; gap:16px; border-bottom:1px solid var(--line); }
    h1 { margin:0; font-size:clamp(2rem, 5vw, 4rem); letter-spacing:0; line-height:.96; }
    p { color:var(--muted); }
    .login, .toolbar, .lead { border:1px solid var(--line); border-radius:8px; background:var(--panel); }
    .login { display:grid; gap:12px; max-width:460px; padding:18px; margin-bottom:18px; }
    input, select, button { min-height:42px; border-radius:8px; border:1px solid var(--line); font:inherit; }
    input, select { width:100%; padding:0 12px; background:#0f1210; color:var(--ink); }
    button { padding:0 14px; background:var(--green); color:#061109; font-weight:900; cursor:pointer; }
    button.secondary { background:rgba(255,255,255,.1); color:var(--ink); }
    .toolbar { display:flex; flex-wrap:wrap; align-items:center; justify-content:space-between; gap:12px; padding:14px; margin-bottom:16px; }
    .grid { display:grid; gap:12px; }
    .lead { padding:16px; }
    .lead-head { display:flex; flex-wrap:wrap; justify-content:space-between; gap:12px; margin-bottom:10px; }
    .pill { display:inline-flex; align-items:center; min-height:28px; padding:0 9px; border-radius:999px; background:rgba(54,208,111,.16); color:var(--green); font-size:.82rem; font-weight:900; }
    .pill.new { background:rgba(217,164,65,.16); color:var(--yellow); }
    code { color:var(--green); word-break:break-all; }
    .muted { color:var(--muted); }
    .actions { display:flex; flex-wrap:wrap; gap:8px; margin-top:12px; }
  </style>
</head>
<body>
  <header>
    <div>
      <p>Niharika wholesale control room</p>
      <h1>Admin Leads</h1>
    </div>
  </header>
  <main>
    <form id="login" class="login">
      <label>Admin token <input id="token" type="password" placeholder="Enter secure admin token" required></label>
      <button type="submit">Open Dashboard</button>
      <p class="muted">Shows Nina buyer requirements, detected signals, and follow-up status.</p>
    </form>
    <section id="dashboard" hidden>
      <div class="toolbar">
        <strong id="count">0 leads</strong>
        <button class="secondary" id="refresh" type="button">Refresh</button>
      </div>
      <div id="leads" class="grid"></div>
    </section>
  </main>
  <script>
    const login = document.querySelector("#login");
    const tokenInput = document.querySelector("#token");
    const dashboard = document.querySelector("#dashboard");
    const leadsNode = document.querySelector("#leads");
    const countNode = document.querySelector("#count");
    const refresh = document.querySelector("#refresh");
    let adminToken = "";

    async function api(path, payload) {
      const response = await fetch(path, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ admin_token: adminToken, ...payload })
      });
      const data = await response.json();
      if (!response.ok) throw new Error(data.error || "Request failed");
      return data;
    }

    function renderLead(lead) {
      const signals = ((lead.requirements || {}).detected_signals || []).join(", ") || "none";
      const contact = [lead.buyer_email, lead.buyer_phone].filter(Boolean).join(" / ") || "No contact captured";
      return `
        <article class="lead">
          <div class="lead-head">
            <div>
              <strong>${lead.buyer_name || "Unknown buyer"}</strong>
              <div class="muted">${contact}</div>
            </div>
            <span class="pill ${lead.status === "new" ? "new" : ""}">${lead.status}</span>
          </div>
          <p>${lead.message || ""}</p>
          <p class="muted">Buyer type: ${lead.buyer_type || ""} / Signals: <code>${signals}</code></p>
          <p class="muted">Nina reply: ${lead.reply || ""} ${lead.next_question || ""}</p>
          <div class="actions">
            <button type="button" data-id="${lead.id}" data-status="contacted">Mark Contacted</button>
            <button type="button" data-id="${lead.id}" data-status="converted">Mark Converted</button>
            <button class="secondary" type="button" data-id="${lead.id}" data-status="closed">Close</button>
          </div>
        </article>`;
    }

    async function loadLeads() {
      const data = await api("/api/admin/leads", {});
      countNode.textContent = `${data.leads.length} leads`;
      leadsNode.innerHTML = data.leads.map(renderLead).join("") || "<p>No leads yet.</p>";
    }

    login.addEventListener("submit", async (event) => {
      event.preventDefault();
      adminToken = tokenInput.value.trim();
      await loadLeads();
      login.hidden = true;
      dashboard.hidden = false;
    });

    refresh.addEventListener("click", loadLeads);
    leadsNode.addEventListener("click", async (event) => {
      const button = event.target.closest("button[data-id]");
      if (!button) return;
      await api("/api/admin/lead/update", { lead_id: button.dataset.id, status: button.dataset.status });
      await loadLeads();
    });
  </script>
</body>
</html>"""


SURVEY_HTML = """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Niharika Wholesale Survey</title>
  <style>
    :root { color-scheme: dark; --bg:#080a09; --panel:#171b18; --ink:#f7f8f4; --muted:#aeb8af; --line:rgba(255,255,255,.12); --green:#36d06f; }
    * { box-sizing:border-box; }
    body { margin:0; font-family:Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; color:var(--ink); background:var(--bg); }
    main { min-height:100vh; display:grid; grid-template-columns:minmax(0,.75fr) minmax(340px,1fr); gap:clamp(22px,5vw,70px); padding:clamp(24px,6vw,76px); align-items:start; }
    h1 { margin:0; font-size:clamp(2.6rem,7vw,5.7rem); line-height:.94; letter-spacing:0; }
    p { color:var(--muted); font-size:1.04rem; }
    form, .panel { display:grid; gap:12px; padding:20px; border:1px solid var(--line); border-radius:8px; background:var(--panel); }
    .grid { display:grid; grid-template-columns:repeat(2,minmax(0,1fr)); gap:12px; }
    label { display:grid; gap:6px; color:var(--muted); font-size:.92rem; font-weight:750; }
    input, select, textarea, button { border:1px solid var(--line); border-radius:8px; font:inherit; }
    input, select { min-height:44px; padding:0 12px; background:#0f1210; color:var(--ink); }
    textarea { min-height:110px; padding:12px; resize:vertical; background:#0f1210; color:var(--ink); }
    button, a.button { display:inline-flex; align-items:center; justify-content:center; min-height:44px; padding:0 16px; border:0; border-radius:999px; background:var(--green); color:#061109; font-weight:900; text-decoration:none; cursor:pointer; }
    .muted { color:var(--muted); }
    .success { border-color:rgba(54,208,111,.45); }
    @media (max-width:840px) { main, .grid { grid-template-columns:1fr; } }
  </style>
</head>
<body>
  <main>
    <section>
      <p>Niharika wholesale requirement survey</p>
      <h1>Tell Nina what you need.</h1>
      <p>Share your wholesale order number, business name, category, pieces required, budget, delivery city, and timeline. Niharika will use this to prepare the right wholesale follow-up.</p>
      <div class="panel">
        <strong>Data storage</strong>
        <span class="muted">Your response is saved in Niharika's local lead system and can also be sent to Google Sheets when connected.</span>
      </div>
    </section>
    <section>
      <form id="survey-form">
        <div class="grid">
          <label>Wholesale order no * <input name="wholesale_order_no" required placeholder="WHO-1001"></label>
          <label>Name * <input name="name" required></label>
          <label>Phone / WhatsApp * <input name="phone" required></label>
          <label>Email <input name="email" type="email"></label>
          <label>Name of the business * <input name="business_name" required></label>
          <label>Instagram handle <input name="instagram_handle" placeholder="@yourbrand"></label>
          <label>Buyer type
            <select name="buyer_type">
              <option value="wholesale buyer">Wholesale buyer</option>
              <option value="reseller">Reseller</option>
              <option value="shop owner">Shop owner</option>
              <option value="boutique">Boutique</option>
            </select>
          </label>
          <label>Main category *
            <select name="product_category" required>
              <option value="Sarees">Sarees</option>
              <option value="Kurtis">Kurtis</option>
              <option value="Crop tops">Crop tops</option>
            </select>
          </label>
          <label>Pieces required * <input name="pieces_required" required placeholder="100 pieces"></label>
          <label>Budget <input name="budget" placeholder="Rs. 10,000, Rs. 150/piece, etc."></label>
          <label>Delivery city * <input name="delivery_city" required></label>
          <label>Timeline <input name="timeline" placeholder="This week, 15 days, monthly, etc."></label>
        </div>
        <label>Requirement details <textarea name="requirements" placeholder="Tell Nina anything specific: quality, color, size, urgency, resale plan, etc."></textarea></label>
        <button type="submit">Submit Requirement</button>
      </form>
      <div id="result" class="panel" hidden></div>
    </section>
  </main>
  <script>
    const form = document.querySelector("#survey-form");
    const result = document.querySelector("#result");
    form.addEventListener("submit", async (event) => {
      event.preventDefault();
      const payload = Object.fromEntries(new FormData(form).entries());
      const response = await fetch("/api/survey/submit", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });
      const data = await response.json();
      result.hidden = false;
      result.classList.toggle("success", response.ok);
      if (!response.ok) {
        result.textContent = data.error || "Could not save response.";
        return;
      }
      const whatsappButton = data.response.whatsapp_url
        ? `<a class="button" href="${data.response.whatsapp_url}" target="_blank" rel="noopener">Send to WhatsApp</a>`
        : `<span class="muted">WhatsApp: set NIHARIKA_WHATSAPP_NUMBER to enable direct sending.</span>`;
      result.innerHTML = `<strong>Saved successfully.</strong><span class="muted">Reference: ${data.response.id}</span><span class="muted">Google Sheets: ${data.response.google_sheets.sent ? "sent" : "not connected or not sent"}</span>${whatsappButton}`;
      form.reset();
    });
  </script>
</body>
</html>"""


CUSTOMER_LOGIN_HTML = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Niharika Customer Sign In</title>
  <script src="https://accounts.google.com/gsi/client" async defer></script>
  <style>
    :root {{ color-scheme: dark; --bg:#080a09; --panel:#171b18; --ink:#f7f8f4; --muted:#aeb8af; --line:rgba(255,255,255,.12); --green:#36d06f; }}
    * {{ box-sizing:border-box; }}
    body {{ margin:0; min-height:100vh; display:grid; place-items:center; padding:24px; font-family:Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; color:var(--ink); background:var(--bg); }}
    main {{ width:min(720px,100%); display:grid; gap:16px; }}
    .panel {{ padding:clamp(20px,5vw,36px); border:1px solid var(--line); border-radius:8px; background:var(--panel); }}
    h1 {{ margin:0; font-size:clamp(2.2rem,7vw,4.8rem); line-height:.96; letter-spacing:0; }}
    p {{ color:var(--muted); }}
    code {{ color:var(--green); word-break:break-all; }}
    .success {{ border-color:rgba(54,208,111,.5); }}
    a {{ color:var(--green); }}
  </style>
</head>
<body>
  <main>
    <section class="panel">
      <p>Niharika customer access</p>
      <h1>Sign in with Google</h1>
      <p>Customers can use Google SSO before submitting wholesale surveys, talking to Nina, or accessing business tools.</p>
      <div id="setup"></div>
      <div id="g_id_onload"
        data-client_id="{GOOGLE_CLIENT_ID}"
        data-callback="handleGoogleSignIn"
        data-auto_prompt="false"></div>
      <div class="g_id_signin"
        data-type="standard"
        data-size="large"
        data-theme="filled_black"
        data-text="signin_with"
        data-shape="pill"
        data-logo_alignment="left"></div>
    </section>
    <section id="result" class="panel" hidden></section>
  </main>
  <script>
    const hasClientId = {json.dumps(bool(GOOGLE_CLIENT_ID))};
    const setup = document.querySelector("#setup");
    const result = document.querySelector("#result");

    if (!hasClientId) {{
      setup.innerHTML = `<p><strong>Setup needed:</strong> set <code>GOOGLE_CLIENT_ID</code> and restart Niharika.</p>`;
      document.querySelector(".g_id_signin").style.display = "none";
    }}

    async function handleGoogleSignIn(response) {{
      const apiResponse = await fetch("/api/auth/google", {{
        method: "POST",
        headers: {{ "Content-Type": "application/json" }},
        body: JSON.stringify({{ credential: response.credential }})
      }});
      const data = await apiResponse.json();
      result.hidden = false;
      result.classList.toggle("success", apiResponse.ok);
      if (!apiResponse.ok) {{
        result.innerHTML = `<strong>Sign-in failed</strong><p>${{data.error || "Could not sign in."}}</p>`;
        return;
      }}
      result.innerHTML = `<strong>Signed in</strong><p>Welcome ${{data.customer.name || data.customer.email}}</p><p><code>${{data.customer.email}}</code></p><p><a href="/survey">Continue to wholesale survey</a></p>`;
    }}
  </script>
</body>
</html>"""


class NiharikaWholesaleHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed_url = urlparse(self.path)
        path = parsed_url.path.rstrip("/") or "/"
        query = parse_qs(parsed_url.query)
        if path == "/robots.txt":
            self.send_text("User-agent: *\nAllow: /\nSitemap: https://www.niharika.com/sitemap.xml\n", "text/plain")
            return

        if path == "/sitemap.xml":
            self.send_text(SITEMAP_XML, "application/xml")
            return

        if path == "/api/coursera-blogs":
            payload = {
                "source": COURSERA_BLOG_FEED,
                "updated": datetime.now(timezone.utc).isoformat(),
                "posts": get_coursera_posts(),
            }
            self.send_text(json.dumps(payload), "application/json")
            return

        if path == "/api/edtech-integrations":
            payload = {
                "updated": datetime.now(timezone.utc).isoformat(),
                "integrations": EDTECH_APIS,
            }
            self.send_text(json.dumps(payload), "application/json")
            return

        if path == "/api/topmate-mentors":
            payload = {
                "updated": datetime.now(timezone.utc).isoformat(),
                "filter": "public profiles with 7+ years experience signals",
                "mentors": TOPMATE_MENTORS,
            }
            self.send_text(json.dumps(payload), "application/json")
            return

        if path == "/api/catalog":
            self.send_json({"items": load_catalog()})
            return

        if path == "/api/loom-media":
            self.send_json({"items": list_loom_media()})
            return

        if path == "/api/short-film-media":
            self.send_json({"items": list_short_film_media()})
            return

        if path == "/api/free/catalog":
            self.send_json(
                {
                    "free_api": True,
                    "usage": "Use this public catalogue API for wholesale or retail discovery. No license required.",
                    "items": load_catalog(),
                }
            )
            return

        if path.startswith("/catalog-images/"):
            self.send_catalog_image(path)
            return

        if path.startswith("/media/"):
            self.send_media_file(path)
            return

        if path in {"/algorithms", "/edtech-apis", "/mentors", "/algorithms.html", "/edtech-apis.html", "/mentors.html"}:
            self.send_response(302)
            self.send_header("Location", "/")
            self.end_headers()
            return

        if path in {"/", "/index.html"}:
            self.send_html(static_home_html())
            return

        if path == "/signup":
            self.send_html(SIGNUP_HTML)
            return

        if path == "/admin":
            self.send_html(ADMIN_HTML)
            return

        if path == "/survey":
            self.send_html(SURVEY_HTML)
            return

        if path == "/customer-login":
            self.send_html(CUSTOMER_LOGIN_HTML)
            return

        if path == "/survey-responses.csv":
            token = (query.get("token") or [""])[0]
            if token != NIHARIKA_ADMIN_TOKEN:
                self.send_json({"error": "Invalid admin token."}, 401)
                return
            self.send_text(survey_csv_content(), "text/csv")
            return

        self.send_error(404, "Page not found")

    def do_POST(self):
        path = urlparse(self.path).path.rstrip("/") or "/"
        payload = self.read_json_body()

        if path == "/api/business/signup":
            business, error = create_business(payload)
            if error:
                self.send_json({"error": error}, 400)
                return
            self.send_json(
                {
                    "business": public_business_record(business),
                    "payment_link": payment_link_for_business(business),
                    "payment_whatsapp_url": payment_whatsapp_url(business),
                    "payment_instruction": payment_instruction_for_business(),
                    "message": "First month is free. Connect Shopify, set up payment for later billing, and complete Instagram verification to activate API access.",
                },
                201,
            )
            return

        if path == "/api/auth/google":
            customer, error = sign_in_customer_with_google(payload)
            if error:
                self.send_json({"error": error}, 401)
                return
            self.send_json({"customer": public_customer_record(customer)})
            return

        if path == "/api/business/signin":
            business = sign_in_business(payload)
            if not business:
                self.send_json({"error": "Invalid email or password."}, 401)
                return
            self.send_json(
                {
                    "business": public_business_record(business),
                    "payment_link": payment_link_for_business(business),
                    "payment_whatsapp_url": payment_whatsapp_url(business),
                    "payment_instruction": payment_instruction_for_business(),
                }
            )
            return

        if path == "/api/shopify/connect":
            business, error = connect_shopify_store(payload)
            if error:
                self.send_json({"error": error}, 400)
                return
            self.send_json(
                {
                    "business": public_business_record(business),
                    "message": "Shopify store connected. Recommendations can now return Shopify product/search URLs.",
                }
            )
            return

        if path == "/api/admin/business/update":
            business, error = admin_update_business(payload)
            if error:
                self.send_json({"error": error}, 401)
                return
            self.send_json({"business": public_business_record(business)})
            return

        if path == "/api/admin/leads":
            if payload.get("admin_token") != NIHARIKA_ADMIN_TOKEN:
                self.send_json({"error": "Invalid admin token."}, 401)
                return
            self.send_json({"leads": load_leads()})
            return

        if path == "/api/admin/lead/update":
            if payload.get("admin_token") != NIHARIKA_ADMIN_TOKEN:
                self.send_json({"error": "Invalid admin token."}, 401)
                return
            lead, error = update_lead_status(payload)
            if error:
                self.send_json({"error": error}, 400)
                return
            self.send_json({"lead": lead})
            return

        if path == "/api/admin/surveys":
            if payload.get("admin_token") != NIHARIKA_ADMIN_TOKEN:
                self.send_json({"error": "Invalid admin token."}, 401)
                return
            self.send_json({"responses": load_survey_responses()})
            return

        if path == "/api/license/verify":
            license_key = extract_license_key(self.headers, payload)
            record = get_license_record(license_key)
            active = is_license_active(record)
            self.send_json(
                {
                    "valid": active,
                    "license": public_license_record(record) if active else None,
                },
                200 if active else 401,
            )
            return

        if path == "/api/free/recommend":
            recommendations = free_retail_wholesale_rank(payload)
            self.send_json(
                {
                    "free_api": True,
                    "request_type": payload.get("request_type") or payload.get("buyer_type") or "wholesale",
                    "recommendations": recommendations,
                    "best_pick": recommendations[0] if recommendations else None,
                    "contact": {
                        "email": "sivashankarimurugesan@niharika.com",
                        "instagram": NIHARIKA_INSTAGRAM_URL,
                    },
                }
            )
            return

        if path == "/api/free/requirements":
            self.send_json(free_requirement_payload(payload), 201)
            return

        if path == "/api/free/chat":
            self.send_json(niharika_api_chat(payload))
            return

        if path == "/api/free/survey":
            response, error = save_survey_response({**payload, "source": payload.get("source") or "niharika-free-api"})
            if error:
                self.send_json(error, 400)
                return
            self.send_json({"free_api": True, "response": response}, 201)
            return

        if path == "/api/recommend":
            license_key = extract_license_key(self.headers, payload)
            record = get_license_record(license_key)
            if not is_license_active(record):
                self.send_json({"error": "Active Niharika business license required."}, 401)
                return

            business = get_business_by_license_key(license_key)
            if business and not payload.get("shopify_store_domain"):
                payload["shopify_store_domain"] = business.get("shopify_store_domain", "")
            recommendations = rank_recommendations(payload)
            self.send_json(
                {
                    "license": public_license_record(record),
                    "shopify_store_domain": payload.get("shopify_store_domain", ""),
                    "recommendations": recommendations,
                    "best_pick": recommendations[0] if recommendations else None,
                }
            )
            return

        if path == "/api/nina/requirements":
            result = connected_nina_requirement_reply(payload)
            lead = save_lead(payload, result)
            result["lead"] = lead
            self.send_json(result)
            return

        if path == "/api/survey/submit":
            response, error = save_survey_response(payload)
            if error:
                self.send_json(error, 400)
                return
            self.send_json({"response": response}, 201)
            return

        self.send_error(404, "API route not found")

    def read_json_body(self):
        length = int(self.headers.get("Content-Length", 0) or 0)
        if length == 0:
            return {}
        raw_body = self.rfile.read(length).decode("utf-8")
        try:
            return json.loads(raw_body)
        except json.JSONDecodeError:
            return {}

    def send_html(self, html):
        self.send_text(html, "text/html")

    def send_json(self, payload, status=200):
        self.send_text(json.dumps(payload), "application/json", status)

    def send_catalog_image(self, path):
        filename = os.path.basename(path)
        if not filename or filename != path.rsplit("/", 1)[-1]:
            self.send_error(404, "Image not found")
            return
        image_path = os.path.abspath(os.path.join(catalog_images_dir(), filename))
        image_root = os.path.abspath(catalog_images_dir())
        if not image_path.startswith(image_root) or not os.path.exists(image_path):
            self.send_error(404, "Image not found")
            return
        content_type = mimetypes.guess_type(image_path)[0] or "application/octet-stream"
        with open(image_path, "rb") as image_file:
            body = image_file.read()
        self.send_response(200)
        self.send_security_headers()
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def send_media_file(self, path):
        relative_path = unquote(path[len("/media/") :]).replace("\\", "/")
        if not relative_path:
            self.send_error(404, "Media not found")
            return
        normalized = os.path.normpath(relative_path)
        if normalized.startswith("..") or os.path.isabs(normalized):
            self.send_error(404, "Media not found")
            return
        media_path = os.path.abspath(os.path.join(media_dir(), normalized))
        media_root = os.path.abspath(media_dir())
        if not media_path.startswith(media_root) or not os.path.isfile(media_path):
            self.send_error(404, "Media not found")
            return
        content_type = mimetypes.guess_type(media_path)[0] or "application/octet-stream"
        with open(media_path, "rb") as media_file:
            body = media_file.read()
        self.send_response(200)
        self.send_security_headers()
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def allowed_origin(self):
        origin = self.headers.get("Origin", "")
        allowed_origins = {
            "http://127.0.0.1:8080",
            "http://localhost:8080",
            "https://www.niharika.com",
            "https://nina.niharika.com",
        }
        if origin in allowed_origins:
            return origin
        return ""

    def send_security_headers(self):
        origin = self.allowed_origin()
        if origin:
            self.send_header("Access-Control-Allow-Origin", origin)
            self.send_header("Vary", "Origin")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("X-Frame-Options", "DENY")
        self.send_header("Referrer-Policy", "strict-origin-when-cross-origin")
        self.send_header("Permissions-Policy", "camera=(), microphone=(), geolocation=()")
        self.send_header(
            "Content-Security-Policy",
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' https://accounts.google.com; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data: https://images.unsplash.com https://www.instagram.com; "
            "media-src 'self'; "
            "connect-src 'self'; "
            "frame-src https://accounts.google.com; "
            "base-uri 'self'; "
            "form-action 'self' mailto:",
        )

    def send_text(self, text, content_type, status=200):
        body = text.encode("utf-8")
        self.send_response(status)
        self.send_security_headers()
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization, X-Niharika-License")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        if self.path.startswith("/admin") or self.path.startswith("/api/admin") or self.path.startswith("/survey-responses.csv"):
            self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Type", f"{content_type}; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_security_headers()
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization, X-Niharika-License")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.end_headers()

    def log_message(self, format, *args):
        print("%s - %s" % (self.address_string(), format % args))


def run_server():
    server = ThreadingHTTPServer((HOST, PORT), NiharikaWholesaleHandler)
    print(f"{SITE_NAME} is running at http://{HOST}:{PORT}")
    print("Press Ctrl+C to stop the server.")
    server.serve_forever()


if __name__ == "__main__":
    run_server()
