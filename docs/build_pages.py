"""Build the static Job Market Data site (GitHub Pages, folder docs/) from the CSVs in data/.

Pages: home, salary pages per role, company hiring pages, ATS market share, sitemap.xml and robots.txt.
The interactive Salary Explorer (docs/explorer.html) is built by docs/build_site.py.

Run from the repo root:  python docs/build_pages.py
"""
from __future__ import annotations

import csv
import html
import json
import re
import shutil
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs"
DATA = ROOT / "data"
BASE = "https://ekkysoka7-maker.github.io/job-market-data-examples"
SUITE = "https://apify.com/worthwhile_quinsy"
KAGGLE = "https://www.kaggle.com/datasets/ekkysoka/startup-hiring-and-salary-benchmarks-2026"
REPO = "https://github.com/ekkysoka7-maker/job-market-data-examples"
SNAPSHOT = "October 2026"
SNAPSHOT_ISO = "2026-10-04"
# Per-ATS scrapers that are live on the Apify Store. Add an ATS here once its Actor is published.
PUBLISHED_ATS = {"greenhouse", "lever", "ashby", "workable", "workday"}
ATS_NAMES = {"greenhouse": "Greenhouse", "lever": "Lever", "ashby": "Ashby", "workable": "Workable",
             "smartrecruiters": "SmartRecruiters", "recruitee": "Recruitee", "bamboohr": "BambooHR",
             "personio": "Personio", "workday": "Workday"}
CUR = {"USD": "$", "GBP": "£", "EUR": "€", "CAD": "CA$"}
COUNTRY = {"US": "United States", "CA": "Canada", "GB": "United Kingdom", "IE": "Ireland",
           "Multiple": "several countries", "Remote": "remote (no country)"}

esc = html.escape


def slug(text: str) -> str:
    s = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return s or "item"


def place(r: dict) -> str:
    if r["country"] == "Multiple":
        return f"Multiple countries ({r['cur']})"
    return COUNTRY.get(r["country"], r["country"])


def money(v: float, cur: str) -> str:
    return f"{CUR.get(cur, cur + ' ')}{round(v / 1000):,}k"


def pct(v: float) -> str:
    return f"{round(v * 100)}%"


CSS = """
:root{--bg:#f7f8fa;--card:#fff;--ink:#111827;--muted:#6b7280;--line:#e5e7eb;--accent:#2563eb;--band:#bfdbfe;--good:#047857}
@media (prefers-color-scheme:dark){:root{--bg:#0b1020;--card:#121a2e;--ink:#e5e7eb;--muted:#9ca3af;--line:#243049;--accent:#60a5fa;--band:#1e3a8a;--good:#34d399}}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font:16px/1.6 system-ui,-apple-system,Segoe UI,Roboto,sans-serif}
a{color:var(--accent)}header,main,footer{max-width:980px;margin:0 auto;padding:0 16px}
header{display:flex;flex-wrap:wrap;gap:6px 18px;align-items:center;padding-top:18px;font-size:15px}
header .brand{font-weight:700;color:var(--ink);text-decoration:none;margin-right:auto}
main{padding-top:20px;padding-bottom:48px}
h1{font-size:clamp(26px,4.2vw,38px);line-height:1.15;margin:8px 0 10px}h2{font-size:22px;margin:32px 0 10px}
.lead{color:var(--muted);max-width:740px;margin:0 0 20px}
.crumbs{font-size:14px;color:var(--muted)}.crumbs a{color:var(--muted)}
.stats{display:grid;grid-template-columns:repeat(auto-fit,minmax(170px,1fr));gap:12px;margin:18px 0}
.stat{background:var(--card);border:1px solid var(--line);border-radius:14px;padding:14px 16px}
.stat b{display:block;font-size:24px;font-variant-numeric:tabular-nums}.stat span{color:var(--muted);font-size:14px}
.card{background:var(--card);border:1px solid var(--line);border-radius:14px;overflow-x:auto}
table{width:100%;border-collapse:collapse}th,td{padding:9px 12px;text-align:left;border-bottom:1px solid var(--line);font-variant-numeric:tabular-nums}
th{font-size:13px;color:var(--muted);font-weight:600}td.num,th.num{text-align:right}tr:last-child td{border-bottom:0}
.cta{margin:28px 0;padding:18px 20px;border:1px solid var(--line);border-left:4px solid var(--accent);border-radius:14px;background:var(--card)}
.cta strong{display:block;margin-bottom:4px}.btn{display:inline-block;margin:8px 8px 0 0;padding:8px 14px;border-radius:10px;background:var(--accent);color:#fff;text-decoration:none;font-weight:600}
.btn.alt{background:transparent;color:var(--accent);border:1px solid var(--accent)}
.grid{columns:3 220px;column-gap:24px}.grid a{display:block;padding:3px 0;break-inside:avoid}
.muted{color:var(--muted)}.up{color:var(--good);font-weight:600}
footer{color:var(--muted);font-size:14px;padding-bottom:40px;border-top:1px solid var(--line);padding-top:16px}
"""


def page(path: str, title: str, desc: str, body: str, jsonld: list | None = None) -> None:
    depth = path.count("/")
    up = "../" * depth
    ld = "".join(f'<script type="application/ld+json">{json.dumps(x, separators=(",", ":"))}</script>'
                 for x in (jsonld or []))
    canonical = f"{BASE}/{path}".replace("/index.html", "/")
    doc = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)}</title><meta name="description" content="{esc(desc)}">
<link rel="canonical" href="{canonical}"><meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(desc)}"><meta property="og:type" content="website">
<style>{CSS}</style>{ld}</head><body>
<header><a class="brand" href="{up}index.html">Job Market Data</a>
<a href="{up}salaries/index.html">Salaries</a><a href="{up}companies/index.html">Who is hiring</a>
<a href="{up}ats/index.html">ATS share</a><a href="{up}explorer.html">Salary Explorer</a></header>
<main>{body}</main>
<footer>Data: public job postings read from company job boards (Greenhouse, Ashby, Lever, SmartRecruiters, Workable and
others), snapshot {SNAPSHOT}. Pay is the midpoint of each published range; a posted range is not an offer.
Free CSV: <a href="{KAGGLE}">Kaggle</a> · Code: <a href="{REPO}">GitHub</a> · Live data:
<a href="{SUITE}">Apify</a>.</footer></body></html>
"""
    out = DOCS / path
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(doc, encoding="utf-8")
    PAGES.append(canonical)


PAGES: list[str] = []


def cta_salary(role: str) -> str:
    return f"""<div class="cta"><strong>Need {esc(role)} pay data for another country, seniority or company?</strong>
The Tech Salary Data API returns live median, P25 and P75 pay for any role from company job boards, refreshed daily.
<br><a class="btn" href="{SUITE}/tech-salary-data-api">Get live salary data</a>
<a class="btn alt" href="{SUITE}/ats-jobs-search">Search open {esc(role)} jobs</a></div>"""


def build_salaries(rows: list[dict]) -> dict[str, str]:
    by_role: dict[str, list[dict]] = defaultdict(list)
    for r in rows:
        by_role[r["role"]].append(r)
    us = sorted((r for r in rows if r["country"] == "US"), key=lambda r: -r["m"])
    us_rank = {r["role"]: i + 1 for i, r in enumerate(us)}
    swe = next((r for r in us if r["role"] == "Software Engineer"), None)
    links = {role: f"salaries/{slug(role)}.html" for role in by_role}

    for role, rs in by_role.items():
        rs.sort(key=lambda r: -r["n"])
        main = next((r for r in rs if r["country"] == "US"), rs[0])
        where = place(main) if main["country"] != "Multiple" else f"several countries ({main['cur']})"
        summary = (f"The median posted salary for a {role} at tech startups in {where} is "
                   f"{money(main['m'], main['cur'])} a year (middle half {money(main['p25'], main['cur'])} to "
                   f"{money(main['p75'], main['cur'])}), based on {main['n']:,} job postings from {main['co']:,} companies "
                   f"that publish a pay range. {pct(main['rem'])} of these postings are remote.")
        facts = []
        if main["country"] == "US" and role in us_rank:
            facts.append(f"Ranks #{us_rank[role]} of {len(us)} startup roles by US median pay in this sample.")
            if swe and role != "Software Engineer":
                diff = (main["m"] - swe["m"]) / swe["m"]
                facts.append(f"That is {abs(round(diff * 100))}% {'above' if diff >= 0 else 'below'} the "
                             f"Software Engineer median ({money(swe['m'], 'USD')}).")
        if main.get("mc"):
            facts.append(f"Company-balanced median (each company counted once): {money(main['mc'], main['cur'])}.")
        if main.get("lo") and main.get("hi"):
            facts.append(f"Average posted range: {money(main['lo'], main['cur'])} to {money(main['hi'], main['cur'])}.")
        table = "".join(f"<tr><td>{esc(place(r))}</td>"
                        f"<td class='num'><b>{money(r['m'], r['cur'])}</b></td>"
                        f"<td class='num'>{money(r['p25'], r['cur'])} to {money(r['p75'], r['cur'])}</td>"
                        f"<td class='num'>{r['n']:,}</td><td class='num'>{r['co']:,}</td>"
                        f"<td class='num'>{pct(r['rem'])}</td></tr>" for r in rs)
        # related roles: shared words first, then closest US pay
        words = set(slug(role).split("-")) - {"and", "of", "the", "senior", "manager", "engineer"}
        related = [o for o in by_role if o != role and words & set(slug(o).split("-"))][:6]
        if main["country"] == "US" and role in us_rank:
            i = us_rank[role] - 1
            for o in us[max(0, i - 4): i + 5]:
                if o["role"] != role and o["role"] not in related:
                    related.append(o["role"])
        related = related[:10]
        rel = "".join(f'<a href="{slug(o)}.html">{esc(o)} salary</a>' for o in related)
        faq = [{"@type": "Question", "name": f"What is the median {role} salary at startups?",
                "acceptedAnswer": {"@type": "Answer", "text": summary}},
               {"@type": "Question", "name": f"How much do most startups pay a {role}?",
                "acceptedAnswer": {"@type": "Answer", "text":
                    f"Half of the postings fall between {money(main['p25'], main['cur'])} and "
                    f"{money(main['p75'], main['cur'])} a year in {where}."}}]
        body = f"""<p class="crumbs"><a href="../index.html">Home</a> › <a href="index.html">Salaries</a> › {esc(role)}</p>
<h1>{esc(role)} salary at tech startups ({SNAPSHOT})</h1><p class="lead">{esc(summary)}</p>
<div class="stats"><div class="stat"><b>{money(main['m'], main['cur'])}</b><span>median, {esc(where)}</span></div>
<div class="stat"><b>{money(main['p25'], main['cur'])}–{money(main['p75'], main['cur'])}</b><span>middle half (P25–P75)</span></div>
<div class="stat"><b>{main['n']:,}</b><span>postings from {main['co']:,} companies</span></div>
<div class="stat"><b>{pct(main['rem'])}</b><span>remote postings</span></div></div>
<p>{' '.join(esc(f) for f in facts)}</p>
<h2>{esc(role)} pay by country</h2><div class="card"><table><thead><tr><th>Country</th><th class="num">Median</th>
<th class="num">P25 to P75</th><th class="num">Postings</th><th class="num">Companies</th><th class="num">Remote</th></tr></thead>
<tbody>{table}</tbody></table></div>
<p class="muted">Yearly pay in local currency, from postings that publish a range (hourly x 2080, monthly x 12). Groups need at
least 5 postings from 3 companies. Sales roles exclude on-target earnings, so these are base-pay figures.</p>
{cta_salary(role)}<h2>Related roles</h2><div class="grid">{rel}</div>"""
        page(links[role], f"{role} Salary at Startups {SNAPSHOT[-4:]}: Median {money(main['m'], main['cur'])} | Job Market Data",
             f"{role} pay at tech startups: median {money(main['m'], main['cur'])}, P25-P75 {money(main['p25'], main['cur'])}"
             f" to {money(main['p75'], main['cur'])} from {main['n']:,} job postings with published salaries.",
             body, [{"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": faq}])

    # index of all roles, sorted by US median
    rows_html = "".join(
        f"<tr><td><a href='{slug(r['role'])}.html'>{esc(r['role'])}</a></td><td class='num'><b>{money(r['m'], 'USD')}</b></td>"
        f"<td class='num'>{money(r['p25'], 'USD')} to {money(r['p75'], 'USD')}</td><td class='num'>{r['n']:,}</td>"
        f"<td class='num'>{pct(r['rem'])}</td></tr>" for r in us)
    others = sorted(set(by_role) - {r["role"] for r in us})
    other_html = "".join(f'<a href="{slug(o)}.html">{esc(o)}</a>' for o in others)
    body = f"""<p class="crumbs"><a href="../index.html">Home</a> › Salaries</p>
<h1>Startup salaries by role ({SNAPSHOT})</h1>
<p class="lead">Median and middle-half pay for {len(by_role)} roles, computed from {sum(r['n'] for r in rows):,} job postings
that publish a pay range on company job boards. Sorted by US median.</p>
<div class="card"><table><thead><tr><th>Role (US)</th><th class="num">Median</th><th class="num">P25 to P75</th>
<th class="num">Postings</th><th class="num">Remote</th></tr></thead><tbody>{rows_html}</tbody></table></div>
{'<h2>Other countries and remote roles</h2><div class="grid">' + other_html + '</div>' if others else ''}
{cta_salary('any role')}"""
    page("salaries/index.html", f"Startup Salaries by Role {SNAPSHOT[-4:]}: {len(by_role)} Roles | Job Market Data",
         f"Startup pay benchmarks for {len(by_role)} roles: median, P25 and P75 from real job postings with published salary ranges.",
         body)
    return links


def build_companies(rows: list[dict]) -> None:
    used: dict[str, int] = {}
    for r in rows:
        s = slug(r["company"])
        used[s] = used.get(s, 0) + 1
        r["slug"] = s if used[s] == 1 else f"{s}-{used[s]}"
    by_ind: dict[str, list[dict]] = defaultdict(list)
    for r in rows:
        by_ind[r["industry"] or ""].append(r)

    for r in rows:
        name, ats = r["company"], r["ats"]
        atsn = ATS_NAMES.get(ats, ats.title())
        last, prev = r["last30"], r["prev30"]
        growth = (f"{last} new roles in the last 30 days, up from {prev} in the 30 days before"
                  if prev else f"{last} new roles in the last 30 days, up from none in the 30 days before")
        mult = f" ({last / prev:.1f}x)" if prev else ""
        teams = [t.strip() for t in r["teams"].split(";") if t.strip()]
        about = []
        if r["industry"]:
            about.append(f"Industry: {r['industry']}")
        if r["team_size"]:
            about.append(f"team size about {int(float(r['team_size'])):,}")
        site = r["website"]
        scraper = (f"{SUITE}/{ats}-jobs-scraper" if ats in PUBLISHED_ATS else f"{SUITE}/ats-jobs-search")
        peers = [o for o in by_ind[r["industry"] or ""] if o is not r][:8] if r["industry"] else []
        if len(peers) < 6:
            peers += [o for o in rows if o is not r and o["ats"] == ats and o not in peers][: 8 - len(peers)]
        peer_html = "".join(f'<a href="{o["slug"]}.html">{esc(o["company"])} jobs</a>' for o in peers)
        summary = (f"{name} has {r['open']:,} open jobs on its {atsn} job board. It posted {growth}{mult}, "
                   f"one of the fastest hiring accelerations among the companies we track. "
                   f"{pct(r['remote'])} of its open roles are remote.")
        body = f"""<p class="crumbs"><a href="../index.html">Home</a> › <a href="index.html">Who is hiring</a> › {esc(name)}</p>
<h1>{esc(name)} is hiring: {r['open']:,} open jobs ({SNAPSHOT})</h1><p class="lead">{esc(summary)}</p>
<div class="stats"><div class="stat"><b>{r['open']:,}</b><span>open jobs</span></div>
<div class="stat"><b class="up">{last:,}</b><span>new roles, last 30 days</span></div>
<div class="stat"><b>{prev:,}</b><span>new roles, 30 days before</span></div>
<div class="stat"><b>{pct(r['remote'])}</b><span>remote</span></div></div>
<h2>Where {esc(name)} is hiring</h2>
<p>{'Top teams: ' + esc(', '.join(teams)) + '.' if teams else 'Team names are not published on this board.'}
{esc('; '.join(about)) + '.' if about else ''} Job board: {esc(atsn)}{' · Website: <a href="' + esc(site) + '" rel="nofollow">' + esc(re.sub(r"^https?://(www\.)?", "", site).rstrip("/")) + '</a>' if site else ''}.</p>
<div class="cta"><strong>Get every open {esc(name)} job with title, location, salary and apply link</strong>
Pulled straight from the company's {esc(atsn)} board, as CSV, Excel or JSON. Set it on a schedule to get new {esc(name)} jobs
as soon as they are posted.<br><a class="btn" href="{scraper}">Get {esc(name)} jobs</a>
<a class="btn alt" href="{SUITE}/company-job-alerts">Alert me about new jobs</a>
<a class="btn alt" href="{SUITE}/company-hiring-trends">See more fast-growing companies</a></div>
{'<h2>Similar companies hiring</h2><div class="grid">' + peer_html + '</div>' if peer_html else ''}"""
        page(f"companies/{r['slug']}.html", f"{name} Jobs: {r['open']:,} Open Roles, Hiring Up{mult or ''} | Job Market Data",
             f"{name} is hiring: {r['open']:,} open jobs, {last} new roles in the last 30 days. Teams, remote share and how to "
             f"get every {name} job as CSV.", body)

    rows_html = "".join(
        f"<tr><td><a href='{r['slug']}.html'>{esc(r['company'])}</a></td><td>{esc(r['industry'] or '-')}</td>"
        f"<td class='num up'>{r['last30']:,}</td><td class='num'>{r['prev30']:,}</td><td class='num'>{r['open']:,}</td>"
        f"<td>{esc(ATS_NAMES.get(r['ats'], r['ats']))}</td></tr>" for r in rows)
    body = f"""<p class="crumbs"><a href="../index.html">Home</a> › Who is hiring</p>
<h1>Startups hiring fastest right now ({SNAPSHOT})</h1>
<p class="lead">{len(rows)} companies whose new job postings jumped in the last 30 days compared with the 30 days before,
read from their own job boards. A hiring burst often follows a funding round or a product launch.</p>
<div class="card"><table><thead><tr><th>Company</th><th>Industry</th><th class="num">New (30 d)</th>
<th class="num">Before</th><th class="num">Open jobs</th><th>Job board</th></tr></thead><tbody>{rows_html}</tbody></table></div>
<div class="cta"><strong>Track which companies are speeding up or slowing down hiring</strong>
Company Hiring Trends ranks thousands of companies by hiring momentum, refreshed daily: useful for sales prospecting,
recruiting and investing.<br><a class="btn" href="{SUITE}/company-hiring-trends">Get hiring trends</a>
<a class="btn alt" href="{SUITE}/companies-hiring-by-tech-stack">Companies hiring by tech stack</a></div>"""
    page("companies/index.html", f"Startups Hiring Fastest {SNAPSHOT}: {len(rows)} Companies | Job Market Data",
         f"{len(rows)} startups whose hiring accelerated in the last 30 days, with open jobs, teams and job boards.", body)


def build_ats(rows: list[dict], companies: list[dict]) -> None:
    total = sum(r["open"] for r in rows)
    rows_html = "".join(
        f"<tr><td>{esc(ATS_NAMES.get(r['ats'], r['ats']))}</td><td class='num'>{r['open']:,}</td>"
        f"<td class='num'><b>{r['share'] * 100:.1f}%</b></td><td>"
        + (f"<a href='{SUITE}/{r['ats']}-jobs-scraper'>{esc(ATS_NAMES.get(r['ats'], r['ats']))} Jobs Scraper</a>"
           if r["ats"] in PUBLISHED_ATS else "<span class='muted'>coming soon</span>") + "</td></tr>" for r in rows)
    by_ats: dict[str, list[dict]] = defaultdict(list)
    for c in companies:
        by_ats[c["ats"]].append(c)
    lists = "".join(
        f"<h2>Fast-growing companies on {esc(ATS_NAMES.get(a, a))}</h2><div class='grid'>"
        + "".join(f'<a href="../companies/{c["slug"]}.html">{esc(c["company"])}</a>' for c in cs[:24]) + "</div>"
        for a, cs in sorted(by_ats.items(), key=lambda x: -len(x[1])))
    body = f"""<p class="crumbs"><a href="../index.html">Home</a> › ATS share</p>
<h1>Which applicant tracking systems do startups use? ({SNAPSHOT})</h1>
<p class="lead">Share of {total:,} open startup jobs by the job board (ATS) they are posted on. Greenhouse and Ashby
together host {(rows[0]['share'] + rows[1]['share']) * 100:.0f}% of open roles in this sample.</p>
<div class="card"><table><thead><tr><th>ATS</th><th class="num">Open jobs</th><th class="num">Share</th><th>Scrape it</th></tr></thead>
<tbody>{rows_html}</tbody></table></div>
<div class="cta"><strong>Find out which ATS any company uses</strong> Give a list of company websites and get their job
board and board URL back.<br><a class="btn" href="{SUITE}/ats-detector">Try ATS Detector</a></div>{lists}"""
    page("ats/index.html", f"ATS Market Share Among Startups {SNAPSHOT}: Greenhouse, Ashby, Lever | Job Market Data",
         f"Which applicant tracking systems startups use: share of {total:,} open jobs on Greenhouse, Ashby, Lever, "
         f"SmartRecruiters, Workable and more.", body)


def build_home(sal: list[dict], comp: list[dict], ats: list[dict]) -> None:
    us = sorted((r for r in sal if r["country"] == "US"), key=lambda r: -r["n"])[:12]
    top = "".join(f"<tr><td><a href='salaries/{slug(r['role'])}.html'>{esc(r['role'])}</a></td>"
                  f"<td class='num'><b>{money(r['m'], 'USD')}</b></td><td class='num'>{r['n']:,}</td></tr>" for r in us)
    hot = "".join(f'<a href="companies/{c["slug"]}.html">{esc(c["company"])} (+{c["last30"]})</a>' for c in [c for c in comp if c["open"] < 1000][:18])
    body = f"""<h1>Job market data from 48,000 startup job postings</h1>
<p class="lead">Free salary benchmarks, the startups hiring fastest, and which job boards they use, read directly from the
public job boards of 1,200+ tech companies. Snapshot {SNAPSHOT}; live data is refreshed daily.</p>
<div class="stats"><div class="stat"><b>{sum(r['n'] for r in sal):,}</b><span>salary data points</span></div>
<div class="stat"><b>{len({r['role'] for r in sal})}</b><span>roles with salary pages</span></div>
<div class="stat"><b>{len(comp)}</b><span>fast-growing companies</span></div>
<div class="stat"><b>{sum(r['open'] for r in ats):,}</b><span>open jobs tracked</span></div></div>
<h2>Most common roles: US startup pay</h2><div class="card"><table><thead><tr><th>Role</th><th class="num">Median</th>
<th class="num">Postings</th></tr></thead><tbody>{top}</tbody></table></div>
<p><a href="salaries/index.html">All {len({r['role'] for r in sal})} roles →</a> · <a href="explorer.html">Interactive Salary Explorer →</a></p>
<h2>Startups hiring fastest</h2><div class="grid">{hot}</div><p><a href="companies/index.html">All {len(comp)} companies →</a></p>
<div class="cta"><strong>Use this data in your own tools</strong> Every number here comes from ready-made data tools on Apify:
pay per result, no code needed, with a free monthly credit.<br>
<a class="btn" href="{SUITE}/ats-jobs-search">Search 48k open jobs</a><a class="btn alt" href="{SUITE}/tech-salary-data-api">Salary API</a>
<a class="btn alt" href="{SUITE}/company-hiring-trends">Hiring trends</a><a class="btn alt" href="{REPO}">Code examples</a></div>"""
    page("index.html", "Job Market Data: Startup Salaries, Hiring Trends and ATS Share (2026)",
         "Free startup salary benchmarks by role, the companies hiring fastest and ATS market share, from 48,000 job "
         "postings on company job boards.", body,
         [{"@context": "https://schema.org", "@type": "Dataset", "name": "Startup Hiring and Salary Benchmarks 2026",
           "description": "Salary benchmarks by role and country, fastest-hiring startups and ATS market share from "
                          "public job postings on company job boards.",
           "url": BASE + "/", "sameAs": KAGGLE, "license": "https://creativecommons.org/licenses/by/4.0/",
           "dateModified": SNAPSHOT_ISO, "creator": {"@type": "Person", "name": "Ekky Soka"}}])


def main() -> None:
    sal = []
    for r in csv.DictReader((DATA / "salary_benchmarks.csv").open(encoding="utf-8")):
        if r["period"] != "year":
            continue
        f = lambda k: float(r[k]) if r.get(k) not in (None, "") else None  # noqa: E731
        sal.append({"role": r["role"], "country": r["country"], "cur": r["currency"], "m": f("salary_median"),
                    "p25": f("salary_p25"), "p75": f("salary_p75"), "mc": f("salary_median_by_company"),
                    "lo": f("salary_min_avg"), "hi": f("salary_max_avg"), "n": int(r["sample_size"]),
                    "co": int(r["companies"]), "rem": float(r["remote_share"])})
    comp = [{"company": r["company"], "website": r["website"], "industry": r["industry"], "team_size": r["team_size"],
             "ats": r["ats"], "open": int(r["open_jobs"]), "last30": int(r["jobs_posted_last_30_days"]),
             "prev30": int(r["jobs_posted_previous_30_days"]), "remote": float(r["remote_share"] or 0),
             "teams": r["top_departments"]}
            for r in csv.DictReader((DATA / "fastest_hiring_companies.csv").open(encoding="utf-8"))]
    comp.sort(key=lambda c: (c["open"] >= 1000, -(c["last30"] / max(c["prev30"], 10)), -c["open"]))
    ats = [{"ats": r["ats"], "open": int(r["open_jobs"]), "share": float(r["share_of_open_jobs"])}
           for r in csv.DictReader((DATA / "ats_market_share.csv").open(encoding="utf-8"))]
    ats.sort(key=lambda r: -r["share"])

    for d in ("salaries", "companies", "ats"):
        shutil.rmtree(DOCS / d, ignore_errors=True)
    build_salaries(sal)
    build_companies(comp)
    build_ats(ats, comp)
    build_home(sal, comp, ats)
    PAGES.append(f"{BASE}/explorer.html")
    sm = "".join(f"<url><loc>{u}</loc><lastmod>{SNAPSHOT_ISO}</lastmod></url>" for u in PAGES)
    (DOCS / "sitemap.xml").write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/'
                                      f'schemas/sitemap/0.9">{sm}</urlset>\n', encoding="utf-8")
    (DOCS / "robots.txt").write_text(f"User-agent: *\nAllow: /\nSitemap: {BASE}/sitemap.xml\n", encoding="utf-8")
    (DOCS / ".nojekyll").write_text("", encoding="utf-8")
    print(f"built {len(PAGES)} pages")


if __name__ == "__main__":
    main()
