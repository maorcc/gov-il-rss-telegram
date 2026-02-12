from curl_cffi import requests

# Check our IP and geolocation
r = requests.get('https://ipinfo.io/json', impersonate='chrome')
print(f"Runner IP info: {r.text}")

# Try the feed
try:
    r2 = requests.get(
        'https://www.gov.il/he/api/PublicationApi/rss/26857f24-4eaa-4032-a39d-5dc66d374ee3',
        impersonate='chrome',
        timeout=15
    )
    print(f"Feed status: {r2.status_code}")
    print(f"Feed headers: {dict(r2.headers)}")
    print(f"Feed body (first 300): {r2.text[:300]}")
except Exception as e:
    print(f"Feed error: {e}")
