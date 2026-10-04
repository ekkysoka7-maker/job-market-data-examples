"""Job market data examples: jobs, salaries and hiring signals from 1,200+ tech companies' job boards.

Setup:
    pip install apify-client
    export APIFY_TOKEN=...   # https://console.apify.com/settings/integrations (free account works)

Run one example:
    python examples.py jobs
    python examples.py salaries
    python examples.py board
    python examples.py trends
    python examples.py ats
"""
from __future__ import annotations

import csv
import os
import sys

from apify_client import ApifyClient

client = ApifyClient(os.environ["APIFY_TOKEN"])


def run(actor: str, run_input: dict) -> list[dict]:
    """Start an Actor, wait for it to finish and return its dataset items."""
    result = client.actor(actor).call(run_input=run_input)
    return list(client.dataset(result["defaultDatasetId"]).iterate_items())


def save_csv(rows: list[dict], path: str) -> None:
    if not rows:
        print("no rows")
        return
    keys = list(dict.fromkeys(k for r in rows for k in r))
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=keys)
        w.writeheader()
        for r in rows:
            w.writerow({k: ", ".join(map(str, v)) if isinstance(v, list) else v for k, v in r.items()})
    print(f"saved {len(rows)} rows to {path}")


def jobs() -> None:
    """Remote Python jobs posted in the last 7 days that publish a salary."""
    rows = run("worthwhile_quinsy/ats-jobs-search", {
        "keywords": ["python", "backend"],
        "remoteOnly": True,
        "postedWithinDays": 7,
        "salaryOnly": True,
        "maxResults": 100,
    })
    for r in rows[:10]:
        print(f"{r['title']} @ {r['company']} | {r.get('salary_text') or ''} | {r['url']}")
    save_csv(rows, "remote_python_jobs.csv")


def salaries() -> None:
    """Salary benchmarks (median, P25, P75) for a few roles in the US and UK."""
    rows = run("worthwhile_quinsy/tech-salary-data-api", {
        "keywords": ["software engineer", "product manager", "data scientist"],
        "countries": ["US", "GB"],
        "groupBy": "role_country",
    })
    for r in rows:
        print(f"{r['role']:<30} {r['country']:<3} {r['currency']} median {r['salary_median']:,} "
              f"(P25 {r['salary_p25']:,} to P75 {r['salary_p75']:,}, n={r['sample_size']})")
    save_csv(rows, "salary_benchmarks.csv")


def board() -> None:
    """Every open job from specific companies' Greenhouse boards (URL or slug)."""
    rows = run("worthwhile_quinsy/greenhouse-jobs-scraper", {
        "boardUrls": ["https://job-boards.greenhouse.io/anthropic", "stripe"],
        "maxResults": 500,
    })
    save_csv(rows, "greenhouse_jobs.csv")


def trends() -> None:
    """Companies whose hiring is accelerating: a sales and investment signal."""
    rows = run("worthwhile_quinsy/company-hiring-trends", {
        "direction": "growing",
        "windowDays": 30,
        "minOpenJobs": 10,
        "maxResults": 50,
    })
    for r in rows[:15]:
        print(f"{r['company']:<30} {r['posted_previous_window']:>3} -> {r['posted_last_window']:>3} new jobs "
              f"| {r.get('top_departments')}")
    save_csv(rows, "hiring_trends.csv")


def ats() -> None:
    """Which applicant tracking system (job board) do these companies use?"""
    rows = run("worthwhile_quinsy/ats-detector", {
        "companyWebsites": ["https://linear.app", "https://www.notion.so", "https://vercel.com"],
    })
    for r in rows:
        print(r)


if __name__ == "__main__":
    examples = {"jobs": jobs, "salaries": salaries, "board": board, "trends": trends, "ats": ats}
    name = sys.argv[1] if len(sys.argv) > 1 else "jobs"
    if name not in examples:
        sys.exit(f"usage: python examples.py [{'|'.join(examples)}]")
    examples[name]()
