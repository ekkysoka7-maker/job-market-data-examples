/**
 * Google Sheets: pull fresh job postings into the active sheet.
 *
 * 1. Extensions > Apps Script, paste this file, save.
 * 2. Project Settings > Script properties: add APIFY_TOKEN (from https://console.apify.com/settings/integrations).
 * 3. Edit SEARCH below, run refreshJobs() once and allow access.
 * 4. Optional: Triggers > Add trigger > refreshJobs, time-driven, daily.
 */
const ACTOR = 'worthwhile_quinsy~ats-jobs-search';
const SEARCH = {
  keywords: ['data engineer'],
  countries: ['US'],
  remoteOnly: true,
  postedWithinDays: 7,
  maxResults: 200,
};
const COLUMNS = ['title', 'company', 'location', 'is_remote', 'seniority', 'salary_min', 'salary_max',
  'salary_currency', 'published_at', 'url'];

function refreshJobs() {
  const token = PropertiesService.getScriptProperties().getProperty('APIFY_TOKEN');
  const url = `https://api.apify.com/v2/acts/${ACTOR}/run-sync-get-dataset-items?token=${token}`;
  const res = UrlFetchApp.fetch(url, {
    method: 'post', contentType: 'application/json', payload: JSON.stringify(SEARCH), muteHttpExceptions: true,
  });
  if (res.getResponseCode() >= 300) throw new Error(res.getContentText());
  const items = JSON.parse(res.getContentText());
  const sheet = SpreadsheetApp.getActiveSheet();
  sheet.clearContents();
  const rows = [COLUMNS].concat(items.map((it) => COLUMNS.map((c) => (it[c] === undefined || it[c] === null ? '' : it[c]))));
  sheet.getRange(1, 1, rows.length, COLUMNS.length).setValues(rows);
  sheet.getRange(1, 1, 1, COLUMNS.length).setFontWeight('bold');
}
