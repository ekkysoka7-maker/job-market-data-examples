# Zapier: new jobs to Slack, email or Sheets

## Option A: Apify app (recommended)

1. Trigger: **Schedule by Zapier > Every Day**.
2. Action: **Apify > Run Actor** (connect your Apify account).
   - Actor: `worthwhile_quinsy/ats-jobs-search` (or any tool listed in the main README)
   - Input JSON: `{ "keywords": ["product manager"], "countries": ["US"], "newWithinDays": 1, "maxResults": 50 }`
   - Wait for finish: `Yes`
3. Action: **Apify > Fetch Dataset Items**, dataset ID from step 2.
4. Action: **Looping by Zapier** over the items, then **Slack > Send Channel Message** or
   **Google Sheets > Create Spreadsheet Row** with `title`, `company`, `location`, `url`.

## Option B: Webhooks by Zapier (no Apify app)

Action **Webhooks by Zapier > Custom Request**:

- Method `POST`
- URL `https://api.apify.com/v2/acts/worthwhile_quinsy~ats-jobs-search/run-sync-get-dataset-items`
- Headers `Authorization: Bearer YOUR_APIFY_TOKEN`, `Content-Type: application/json`
- Data: the same input JSON as above

The response is the list of job rows.

## Ideas

- Daily alert when target companies post new roles: actor `worthwhile_quinsy~company-job-alerts`, input
  `{"companyWebsites": ["https://linear.app", "https://vercel.com"], "newWithinDays": 1}`.
- Monday digest of companies hiring for a technology you sell into: actor
  `worthwhile_quinsy~companies-hiring-by-tech-stack`, input `{"technologies": ["Snowflake"]}`.
