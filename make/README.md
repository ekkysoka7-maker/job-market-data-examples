# Make (Integromat): new jobs to Google Sheets every morning

No code and no Apify app needed: one HTTP request runs the tool and returns the rows.

## Scenario (4 modules)

1. **Schedule**: every day at 08:00.
2. **HTTP > Make a request**
   - URL: `https://api.apify.com/v2/acts/worthwhile_quinsy~ats-jobs-search/run-sync-get-dataset-items`
   - Method: `POST`
   - Headers: `Authorization` = `Bearer YOUR_APIFY_TOKEN` (from https://console.apify.com/settings/integrations)
   - Body type: `Raw`, content type `JSON (application/json)`
   - Request content:
     ```json
     { "keywords": ["data engineer"], "countries": ["US"], "remoteOnly": true, "newWithinDays": 1, "maxResults": 100 }
     ```
   - Parse response: `Yes`. Timeout: 300 seconds.
3. **Iterator**: array = `Data` from module 2.
4. **Google Sheets > Add a row**: map `title`, `company`, `location`, `salary_min`, `salary_max`, `salary_currency`,
   `published_at`, `url`.

`newWithinDays: 1` returns only jobs that appeared since yesterday, so each run adds just the new ones.

## Variations

| Goal | Change in step 2 |
|---|---|
| Jobs from specific companies' Greenhouse boards | URL actor `worthwhile_quinsy~greenhouse-jobs-scraper`, body `{"boardUrls": ["stripe", "https://job-boards.greenhouse.io/anthropic"], "newWithinDays": 1}` |
| Weekly salary benchmarks | actor `worthwhile_quinsy~tech-salary-data-api`, body `{"keywords": ["software engineer"], "countries": ["US"], "groupBy": "role_country"}` |
| Companies speeding up hiring (sales leads) | actor `worthwhile_quinsy~company-hiring-trends`, body `{"direction": "growing", "minOpenJobs": 10, "maxResults": 50}` |
| Post to Slack instead | replace step 4 with **Slack > Create a message**: `{{title}} at {{company}}: {{url}}` |

Cost: pay per result on Apify (about $0.003 per job row); the free monthly Apify credit covers small daily runs.
