import os
import re
import time
from pathlib import Path
from curl_cffi import requests

SENT_FILE = Path(os.environ.get("SENT_FILE", "sent_guids.txt"))
TELEGRAM_BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
TELEGRAM_CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]
RSS_URLS = os.environ["RSS_URLS"].split()
MAX_RETRIES = 5
RETRY_DELAY = 5


def parse_tag(xml, tag):
    m = re.search(f"<{tag}[^>]*>([^<]*)</{tag}>", xml)
    return m.group(1) if m else ""


def fetch_feed(url):
    for attempt in range(1, MAX_RETRIES + 1):
        r = requests.get(url, impersonate="chrome")
        if r.status_code == 200:
            raw = r.content
            if len(raw) >= 2 and (raw[1] == 0 or (raw[0] == 0xFF and raw[1] == 0xFE)):
                return raw.decode("utf-16-le")
            return raw.decode("utf-8")
        print(f"  Attempt {attempt}/{MAX_RETRIES}: HTTP {r.status_code}")
        if attempt < MAX_RETRIES:
            time.sleep(RETRY_DELAY * attempt)
    raise RuntimeError(f"Failed to fetch {url} after {MAX_RETRIES} attempts (last status: {r.status_code})")


def load_sent():
    if SENT_FILE.exists():
        return set(SENT_FILE.read_text().strip().splitlines())
    return set()


def save_sent(guids):
    SENT_FILE.write_text("\n".join(sorted(guids)) + "\n")


def send_telegram(text):
    r = requests.post(
        f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage",
        json={"chat_id": TELEGRAM_CHAT_ID, "text": text, "parse_mode": "HTML"},
    )
    r.raise_for_status()
    return r.json()


def main():
    sent_guids = load_sent()
    new_count = 0
    total_items = 0
    errors = []

    for url in RSS_URLS:
        print(f"Fetching: {url}")
        try:
            xml = fetch_feed(url)
        except RuntimeError as e:
            print(f"  Error: {e}")
            errors.append(str(e))
            continue

        items = xml.split("<item>")[1:]
        total_items += len(items)

        for raw in items:
            item = "<item>" + raw
            guid = parse_tag(item, "guid") or parse_tag(item, "link")
            if not guid or guid in sent_guids:
                continue
            title = parse_tag(item, "title")
            link = parse_tag(item, "link")
            desc = parse_tag(item, "description")
            date = parse_tag(item, "pubDate")
            if not title or not link:
                continue
            print(f"Sending: {title}")
            msg = f"<b>{title}</b>\n\n{desc[:200]}\n\n<a href=\"{link}\">קרא עוד</a>\n\n{date}"
            send_telegram(msg)
            sent_guids.add(guid)
            new_count += 1

    save_sent(sent_guids)
    print(f"Done. Sent {new_count} new items, {total_items} total across {len(RSS_URLS)} feeds.")

    if errors:
        error_msg = "⚠️ gov-il-rss-telegram errors:\n\n" + "\n".join(errors)
        send_telegram(error_msg)
        raise SystemExit(1)


if __name__ == "__main__":
    main()
