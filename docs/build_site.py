"""Build docs/explorer.html (Startup Salary Explorer, for GitHub Pages) from the salary benchmarks CSV.

Run from the examples repo root: python docs/build_site.py [data/salary_benchmarks.csv]
"""
from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SUITE = "https://apify.com/worthwhile_quinsy"


def rows(path: Path) -> list[dict]:
    out = []
    with path.open(encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if r["period"] != "year":
                continue
            out.append({"r": r["role"], "c": r["country"], "cur": r["currency"], "m": int(float(r["salary_median"])),
                        "p25": int(float(r["salary_p25"])), "p75": int(float(r["salary_p75"])),
                        "n": int(r["sample_size"]), "co": int(r["companies"]), "rem": float(r["remote_share"])})
    out.sort(key=lambda x: -x["n"])
    return out


PAGE = r"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Startup Salary Explorer 2026: pay ranges from __N__ job postings</title>
<meta name="description" content="Free startup salary benchmarks: median, P25 and P75 pay by role and country from __N__ job postings with published pay ranges, updated from company job boards.">
<style>
:root{--bg:#f7f8fa;--card:#fff;--ink:#111827;--muted:#6b7280;--line:#e5e7eb;--accent:#2563eb;--band:#bfdbfe}
@media (prefers-color-scheme:dark){:root{--bg:#0b1020;--card:#121a2e;--ink:#e5e7eb;--muted:#9ca3af;--line:#243049;--accent:#60a5fa;--band:#1e3a8a}}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font:16px/1.5 system-ui,-apple-system,Segoe UI,Roboto,sans-serif}
main{max-width:1000px;margin:0 auto;padding:32px 16px 64px}
h1{font-size:clamp(26px,4vw,38px);line-height:1.15;margin:0 0 8px}
.lead{color:var(--muted);margin:0 0 24px;max-width:720px}
.controls{display:flex;flex-wrap:wrap;gap:12px;margin-bottom:16px}
input,select{font:inherit;padding:10px 12px;border:1px solid var(--line);border-radius:10px;background:var(--card);color:var(--ink)}
input{flex:1 1 260px}
.card{background:var(--card);border:1px solid var(--line);border-radius:14px;overflow:hidden}
table{width:100%;border-collapse:collapse}
th,td{padding:10px 12px;text-align:left;border-bottom:1px solid var(--line);font-variant-numeric:tabular-nums}
th{font-size:13px;color:var(--muted);font-weight:600;cursor:pointer;white-space:nowrap;user-select:none}
td.num,th.num{text-align:right}
.bar{position:relative;height:8px;background:var(--line);border-radius:4px;min-width:120px}
.bar span{position:absolute;top:0;bottom:0;background:var(--band);border-radius:4px}
.bar i{position:absolute;top:-3px;width:3px;height:14px;background:var(--accent);border-radius:2px}
.meta{color:var(--muted);font-size:13px;margin:12px 0 0}
.cta{margin-top:32px;padding:20px;border:1px solid var(--line);border-radius:14px;background:var(--card)}
.cta a{color:var(--accent)}
@media (max-width:640px){.hide-sm{display:none}th,td{padding:8px}}
</style>
</head>
<body>
<main>
<p><a href="index.html">← Job Market Data</a></p>
<h1>Startup Salary Explorer</h1>
<p class="lead">What tech startups advertise right now: median, 25th and 75th percentile of posted pay
ranges by role and country, from __N__ job postings with a published salary (snapshot __DATE__).</p>
<div class="controls">
  <input id="q" type="search" placeholder="Search a role, e.g. product manager" aria-label="Search role">
  <select id="country" aria-label="Country"></select>
</div>
<div class="card"><table>
<thead><tr>
  <th data-k="r">Role</th><th data-k="c">Country</th><th class="num" data-k="m">Median</th>
  <th class="hide-sm">P25 to P75</th><th class="num" data-k="n">Postings</th><th class="num hide-sm" data-k="rem">Remote</th>
</tr></thead>
<tbody id="tb"></tbody>
</table></div>
<p class="meta">Pay is the midpoint of each published range, yearly, in local currency (never converted). Groups need at
least 5 postings from 3 companies. The sample leans to US startups; a posted range is not an offer.</p>
<div class="cta">
  <strong>Need fresh numbers for any role, country or company?</strong> The data is refreshed daily from company job
  boards: <a href="__SUITE__/tech-salary-data-api">Tech Salary Data API</a> ·
  <a href="__SUITE__/ats-jobs-search">every open job, filterable</a> ·
  <a href="__SUITE__/company-hiring-trends">who is hiring fastest</a>.
  Free CSV and notebook: <a href="https://www.kaggle.com/datasets/ekkysoka/startup-hiring-and-salary-benchmarks-2026">Kaggle dataset</a>.
</div>
</main>
<script>
const D=__DATA__;
const fmt=(v,c)=>({USD:"$",GBP:"£",EUR:"€",CAD:"CA$"}[c]||c+" ")+Math.round(v/1000)+"k";
let sortK="n",dir=-1;
const sel=document.getElementById("country");
const cs=[...new Set(D.map(x=>x.c))];
sel.innerHTML='<option value="">All countries</option>'+cs.map(c=>`<option ${c==="US"?"selected":""}>${c}</option>`).join("");
function draw(){
  const q=document.getElementById("q").value.toLowerCase().trim(), c=sel.value;
  let rows=D.filter(x=>(!c||x.c===c)&&(!q||x.r.toLowerCase().includes(q)));
  rows.sort((a,b)=>(a[sortK]>b[sortK]?1:a[sortK]<b[sortK]?-1:0)*dir);
  const hi=Math.max(...rows.map(x=>x.p75),1), lo=Math.min(...rows.map(x=>x.p25))*0.85, sp=Math.max(hi-lo,1), pc=v=>(v-lo)/sp*100;
  document.getElementById("tb").innerHTML=rows.map(x=>`<tr><td>${x.r}</td><td>${x.c}</td>
    <td class="num"><strong>${fmt(x.m,x.cur)}</strong></td>
    <td class="hide-sm"><div class="bar" title="${fmt(x.p25,x.cur)} to ${fmt(x.p75,x.cur)}"><span style="left:${pc(x.p25)}%;right:${100-pc(x.p75)}%"></span><i style="left:${pc(x.m)}%"></i></div></td>
    <td class="num">${x.n}</td><td class="num hide-sm">${Math.round(x.rem*100)}%</td></tr>`).join("")||'<tr><td colspan="6">No match</td></tr>';
}
document.querySelectorAll("th[data-k]").forEach(th=>th.onclick=()=>{const k=th.dataset.k;dir=sortK===k?-dir:-1;sortK=k;draw();});
document.getElementById("q").oninput=draw;sel.onchange=draw;draw();
</script>
</body>
</html>
"""


if __name__ == "__main__":
    src = Path(sys.argv[1]) if len(sys.argv) > 1 else HERE.parent / "data" / "salary_benchmarks.csv"
    data = rows(src)
    total = sum(x["n"] for x in data)
    html = (PAGE.replace("__DATA__", json.dumps(data, separators=(",", ":"))).replace("__N__", f"{total:,}")
            .replace("__DATE__", "October 2026").replace("__SUITE__", SUITE))
    (HERE / "explorer.html").write_text(html, encoding="utf-8")
    print("wrote docs/explorer.html with", len(data), "rows,", total, "postings")
