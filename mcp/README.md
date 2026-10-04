# Job Market Data MCP server

Give Claude, ChatGPT, Cursor, Cline or any MCP client live job-market data: open jobs from 1,300+ company job boards,
salary benchmarks, hiring trends, internships, AI jobs and which ATS a company uses. Hosted by Apify, nothing to
install; you need a free Apify account (pay per result, free monthly credit included).

## Remote URL

```
https://mcp.apify.com?tools=worthwhile_quinsy/ats-jobs-search,worthwhile_quinsy/tech-salary-data-api,worthwhile_quinsy/company-hiring-trends,worthwhile_quinsy/ats-detector,worthwhile_quinsy/remote-jobs-api
```

Clients that support remote MCP with OAuth (Claude, Cursor, VS Code) sign you in to Apify the first time. Others can
send the header `Authorization: Bearer YOUR_APIFY_TOKEN`.

## Claude Desktop / Cursor / Cline config

```json
{
  "mcpServers": {
    "job-market-data": {
      "url": "https://mcp.apify.com?tools=worthwhile_quinsy/ats-jobs-search,worthwhile_quinsy/tech-salary-data-api,worthwhile_quinsy/company-hiring-trends,worthwhile_quinsy/ats-detector,worthwhile_quinsy/remote-jobs-api",
      "headers": { "Authorization": "Bearer YOUR_APIFY_TOKEN" }
    }
  }
}
```

## Tools

| Tool | Ask your agent for example |
|---|---|
| Company Jobs Search | "Find remote data engineering jobs in Europe that publish a salary" |
| Tech Salary Data API | "What do US startups pay product managers? Median and range" |
| Company Hiring Trends | "Which fintech startups are hiring faster than last month?" |
| ATS Detector | "Which applicant tracking system do linear.app and vercel.com use?" |
| Remote Jobs API | "List new remote Python jobs from the last 3 days" |

More tools (Greenhouse / Lever / Ashby / Workable / Workday Jobs Scrapers, Internship & New Grad Jobs, AI & ML Jobs,
Y Combinator Startup Jobs) can be added to the `tools=` list: see https://apify.com/worthwhile_quinsy

## Data and privacy

Only public job-posting data from company career pages. No personal data. Runs are billed to your own Apify account.
