# Job Market Data API Examples

Copy-paste examples for getting **job postings, salary benchmarks and hiring signals** from the public job boards of
1,200+ tech companies (Greenhouse, Ashby, Lever, SmartRecruiters, Workable, Recruitee, BambooHR, Personio) in Python,
JavaScript, Google Sheets and n8n.

The data comes from a daily-refreshed database of 48,000+ open jobs, served by ready-made tools on
[Apify](https://apify.com/worthwhile_quinsy). You need a free Apify account and its API token; tools are billed per
result, and the free monthly credit covers trying every example.

| Example | What you get | Tool |
|---|---|---|
| Search jobs | Jobs by title, country, remote, salary, tech stack, date | [Company Jobs Search](https://apify.com/worthwhile_quinsy/ats-jobs-search) |
| Salary benchmarks | Median, P25 and P75 pay by role and country | [Tech Salary Data API](https://apify.com/worthwhile_quinsy/tech-salary-data-api) |
| Scrape a job board | Every open job from given company boards | [Greenhouse](https://apify.com/worthwhile_quinsy/greenhouse-jobs-scraper), [Lever](https://apify.com/worthwhile_quinsy/lever-jobs-scraper), [Ashby](https://apify.com/worthwhile_quinsy/ashby-jobs-scraper), [Workable](https://apify.com/worthwhile_quinsy/workable-jobs-scraper), [Workday](https://apify.com/worthwhile_quinsy/workday-jobs-scraper) |
| Hiring trends | Companies accelerating or slowing hiring | [Company Hiring Trends](https://apify.com/worthwhile_quinsy/company-hiring-trends) |
| Job alerts | New jobs from any company's careers page | [Company Job Alerts](https://apify.com/worthwhile_quinsy/company-job-alerts) |
| ATS detection | Which job board a company uses | [ATS Detector](https://apify.com/worthwhile_quinsy/ats-detector) |
| Remote jobs | Remote jobs API | [Remote Jobs API](https://apify.com/worthwhile_quinsy/remote-jobs-api) |
| AI & ML jobs | ML, LLM and data science roles | [AI & Machine Learning Jobs](https://apify.com/worthwhile_quinsy/ai-machine-learning-jobs-scraper) |
| Early-career jobs | Internships and new-grad roles | [New Grad & Internship Jobs](https://apify.com/worthwhile_quinsy/new-grad-internship-jobs-scraper) |
| YC startup jobs | Open roles at Y Combinator companies | [Y Combinator Startup Jobs](https://apify.com/worthwhile_quinsy/y-combinator-startup-jobs-scraper) |
| Tech stack signals | Companies hiring for a technology | [Companies Hiring by Tech Stack](https://apify.com/worthwhile_quinsy/companies-hiring-by-tech-stack) |

## Python

```bash
pip install apify-client
export APIFY_TOKEN=your_token
python python/examples.py jobs       # remote Python jobs with salary, last 7 days -> CSV
python python/examples.py salaries   # salary benchmarks US + UK -> CSV
python python/examples.py board      # all jobs from given Greenhouse boards -> CSV
python python/examples.py trends     # fastest-growing hiring companies -> CSV
python python/examples.py ats        # which ATS does a company use
```

## JavaScript (Node 18+)

```bash
npm install apify-client
APIFY_TOKEN=your_token node javascript/examples.mjs salaries
```

## Plain HTTP (any language)

One request starts the tool, waits, and returns the rows as JSON:

```bash
curl -X POST "https://api.apify.com/v2/acts/worthwhile_quinsy~ats-jobs-search/run-sync-get-dataset-items?token=$APIFY_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"keywords":["product manager"],"countries":["US"],"salaryOnly":true,"maxResults":50}'
```

## Google Sheets

[`google-sheets/jobs-to-sheet.gs`](google-sheets/jobs-to-sheet.gs) refreshes a sheet with new jobs every day. Setup
steps are at the top of the file.

## n8n

Import a workflow from [`n8n/`](n8n/) (Workflows > Import from file):

- `daily-job-alerts-to-slack.json`: new jobs from chosen companies posted to Slack every morning
- `weekly-tech-stack-buying-signals-to-sheets.json`: companies hiring for a technology, appended to Google Sheets weekly

## Make and Zapier

Step-by-step scenarios: [`make/`](make/README.md) and [`zapier/`](zapier/README.md).

## AI agents (MCP)

Ready-made MCP config and registry file: [`mcp/`](mcp/README.md).

All tools work through [Apify's MCP server](https://mcp.apify.com), so Claude, ChatGPT or Cursor can call them, for
example: "find remote data engineering jobs in Europe that publish a salary".

## Job Market Data website

The [`docs/`](docs) folder is a free static website, published with GitHub Pages at
**https://ekkysoka7-maker.github.io/job-market-data-examples/**: salary pages for 137 startup roles, hiring pages for
187 fast-growing companies, ATS market share and an interactive Salary Explorer. Rebuild it from the CSVs in
[`data/`](data) (same files as the Kaggle dataset):

```bash
python docs/build_site.py    # docs/explorer.html
python docs/build_pages.py   # every other page, sitemap.xml and robots.txt
```

## Free dataset

A snapshot with salary benchmarks for 151 role and country pairs, the 187 fastest-hiring companies and ATS market share
is on Kaggle: https://www.kaggle.com/datasets/ekkysoka/startup-hiring-and-salary-benchmarks-2026

## Notes

Only public job-posting data is used. Please respect the terms of the sites where you use the data and applicable
laws. Issues and requests for new examples are welcome.

License: MIT
