"""Scan all gov.il departments for working RSS feeds and generate FEEDS.md."""
import re
import time
from collections import defaultdict
from curl_cffi import requests

MAX_RETRIES = 3
RETRY_DELAY = 3

API_TYPES = ['PublicationApi', 'NewsApi', 'ServiceApi', 'AlertsApi', 'PolicyApi', 'LegalInfoApi', 'InformationTypeApi']
API_LABELS = {
    "PublicationApi": "פרסומים",
    "NewsApi": "חדשות",
    "ServiceApi": "שירותים",
    "AlertsApi": "התראות",
    "PolicyApi": "מדיניות",
    "LegalInfoApi": "חקיקה",
    "InformationTypeApi": "מדריכים",
}


def fetch_with_retry(url):
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            resp = requests.get(url, impersonate='chrome', timeout=15)
            if resp.status_code == 200:
                return resp
            if attempt < MAX_RETRIES:
                time.sleep(RETRY_DELAY * attempt)
        except Exception:
            if attempt < MAX_RETRIES:
                time.sleep(RETRY_DELAY * attempt)
    return None


def decode_response(raw):
    if len(raw) < 50:
        return None
    if len(raw) >= 2 and (raw[1] == 0 or (raw[0] == 0xFF and raw[1] == 0xFE)):
        return raw.decode('utf-16-le', errors='replace')
    return raw.decode('utf-8', errors='replace')


def generate_feeds_md(departments):
    lines = []
    lines.append('<div dir="rtl">')
    lines.append("")
    lines.append("# ערוצי RSS פעילים באתר gov.il")
    lines.append("")
    total_feeds = sum(len(v) for v in departments.values())
    lines.append(f"רשימה של {total_feeds} ערוצי RSS פעילים ב-{len(departments)} גופים ממשלתיים.")
    lines.append("")
    lines.append("קובץ זה נוצר אוטומטית על ידי `scan_feeds.py`.")
    lines.append("")
    lines.append("<table>")
    header = "<tr><th>גוף</th>"
    for api in API_TYPES:
        header += f"<th>{API_LABELS[api]}</th>"
    header += "</tr>"
    lines.append(header)

    for title in sorted(departments.keys()):
        apis = departments[title]
        row = f"<tr><td>{title}</td>"
        for api in API_TYPES:
            if api in apis:
                row += f'<td><a href="{apis[api]}">{API_LABELS[api]}</a></td>'
            else:
                row += "<td></td>"
        row += "</tr>"
        lines.append(row)

    lines.append("</table>")
    lines.append("")
    lines.append("</div>")
    lines.append("")
    return "\n".join(lines)


r = requests.get('https://www.gov.il/govil-landing-page-api/he', impersonate='chrome')
all_departments = r.json()['results']

print(f'Testing {len(all_departments)} departments x {len(API_TYPES)} feed types...', flush=True)

results = []
for i, dept in enumerate(all_departments):
    slug = dept['urlName']
    guid = dept['offices'][0] if dept.get('offices') else None
    if not guid:
        continue
    print(f'[{i+1}/{len(all_departments)}] {slug}...', end=' ', flush=True)
    found = []
    for api in API_TYPES:
        url = f'https://www.gov.il/he/api/{api}/rss/{guid}'
        resp = fetch_with_retry(url)
        if not resp:
            continue
        text = decode_response(resp.content)
        if not text:
            continue
        item_count = text.count('<item>')
        if item_count > 0:
            results.append((dept['title'], slug, api, item_count, url))
            found.append(f'{api}({item_count})')
        time.sleep(0.05)
    print(', '.join(found) if found else 'none', flush=True)

print(f'\n=== RESULTS: {len(results)} working feeds ===\n', flush=True)
for title, slug, api, count, url in sorted(results, key=lambda x: (x[1], x[2])):
    print(f'{title} | {api} | {count} items | {url}', flush=True)

# Generate FEEDS.md
departments_map = defaultdict(dict)
for title, slug, api, count, url in results:
    departments_map[title][api] = url

md = generate_feeds_md(departments_map)
with open("FEEDS.md", "w") as f:
    f.write(md)
print(f'\nGenerated FEEDS.md: {len(departments_map)} departments, {len(results)} feeds', flush=True)
