// Job market data examples (Node.js 18+).
//
//   npm install apify-client
//   export APIFY_TOKEN=...      # https://console.apify.com/settings/integrations
//   node examples.mjs jobs | salaries | board | trends
import { ApifyClient } from 'apify-client';

const client = new ApifyClient({ token: process.env.APIFY_TOKEN });

async function run(actor, input) {
    const { defaultDatasetId } = await client.actor(actor).call(input);
    const { items } = await client.dataset(defaultDatasetId).listItems();
    return items;
}

const examples = {
    // Remote Python jobs posted in the last 7 days with a published salary
    async jobs() {
        const rows = await run('worthwhile_quinsy/ats-jobs-search', {
            keywords: ['python', 'backend'], remoteOnly: true, postedWithinDays: 7, salaryOnly: true, maxResults: 100,
        });
        for (const r of rows.slice(0, 10)) console.log(`${r.title} @ ${r.company} | ${r.salary_text ?? ''} | ${r.url}`);
    },
    // Median, P25 and P75 pay per role and country
    async salaries() {
        const rows = await run('worthwhile_quinsy/tech-salary-data-api', {
            keywords: ['software engineer', 'product manager'], countries: ['US', 'GB'], groupBy: 'role_country',
        });
        console.table(rows.map(({ role, country, currency, salary_median, salary_p25, salary_p75, sample_size }) =>
            ({ role, country, currency, salary_median, salary_p25, salary_p75, sample_size })));
    },
    // All open jobs from specific Ashby boards
    async board() {
        const rows = await run('worthwhile_quinsy/ashby-jobs-scraper', {
            boardUrls: ['https://jobs.ashbyhq.com/linear', 'notion'], maxResults: 500,
        });
        console.log(`${rows.length} jobs`, rows.slice(0, 5).map((r) => r.title));
    },
    // Companies that are accelerating hiring
    async trends() {
        const rows = await run('worthwhile_quinsy/company-hiring-trends', {
            direction: 'growing', windowDays: 30, minOpenJobs: 10, maxResults: 50,
        });
        console.table(rows.slice(0, 15).map(({ company, posted_previous_window, posted_last_window, trend_score }) =>
            ({ company, posted_previous_window, posted_last_window, trend_score })));
    },
};

const name = process.argv[2] ?? 'jobs';
if (!examples[name]) {
    console.error(`usage: node examples.mjs ${Object.keys(examples).join('|')}`);
    process.exit(1);
}
await examples[name]();
