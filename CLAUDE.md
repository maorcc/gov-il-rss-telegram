# gov-il-rss-telegram

Forwards RSS feed updates from gov.il to Telegram via GitHub Actions.

## Project Structure

- `gov_il_rss.py` - Main script: fetches RSS feeds, detects new items, sends to Telegram
- `.github/workflows/gov-il-rss.yml` - GitHub Actions workflow (runs every 6 hours)
- `scan_feeds.py` - Utility: scans all gov.il departments for working RSS feeds (not part of the workflow)

## Key Details

- Uses `curl_cffi` with Chrome TLS impersonation to bypass Cloudflare blocking on gov.il
- RSS feeds may be UTF-16-LE encoded; the script auto-detects and handles this
- Sent GUIDs are cached in `sent_guids.txt` (persisted via GitHub Actions cache)
- No `pyproject.toml` — dependencies are installed inline via `uv run --no-project --with curl_cffi`

## Environment Variables (GitHub Secrets)

- `TELEGRAM_BOT_TOKEN` - Bot token from @BotFather
- `TELEGRAM_CHAT_ID` - Target chat/group ID
- `RSS_URLS` - Space-separated list of RSS feed URLs

## Running Locally

```bash
export TELEGRAM_BOT_TOKEN="..."
export TELEGRAM_CHAT_ID="..."
export RSS_URLS="https://www.gov.il/he/api/NewsApi/rss/..."
uv run --no-project --with curl_cffi python gov_il_rss.py
```

## Updating FEEDS.md

```bash
uv run --no-project --with curl_cffi python scan_feeds.py
```