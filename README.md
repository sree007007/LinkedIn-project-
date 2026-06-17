# LinkedIn Job Alerts

Near–real-time job alerts. Set keywords + location, and get a **Telegram push**
within minutes of a matching job going live on LinkedIn.

## ⚠️ Read this first — the honest reality

- **There is no "next second" push.** LinkedIn does **not** broadcast an event
  when a job goes live. No app can be notified instantly — it has to *poll*
  (repeatedly ask "what's new?"). Your latency floor = your polling interval.
  This tool targets **minutes**, not seconds, which is the practical ceiling for
  every "instant job alert" product that exists.
- **This uses LinkedIn's public, logged-out "guest" jobs endpoint.** No login,
  no credentials, no account at risk of a logged-in-automation ban. It only sees
  the same public listings a signed-out visitor sees.
- **It still goes against LinkedIn's User Agreement (§8.2, automated access).**
  Use it for personal job-hunting at a respectful rate. LinkedIn can rate-limit,
  change, or block the endpoint at any time. **Keep the polling interval high**
  (default 300s). Hammering it = an instant IP block and is abusive.
- **No detection-evasion is included by design** (no proxy rotation, no CAPTCHA
  solving). If you get blocked, slow down — don't try to evade.
- The job source is **pluggable**. When you're ready, swap the scraper for
  LinkedIn's official Talent Solutions partner API (the only fully compliant
  route) by adding a new class in `src/sources/`.

## How it works

```
poll loop (every INTERVAL seconds)
   │
   ├─ source.fetch(query)        # LinkedIn guest endpoint, last-hour jobs
   ├─ store.filter_new(jobs)     # SQLite dedupe — skip jobs already seen
   ├─ matcher.matches(job)       # include/exclude keywords + location
   └─ notifier.send(job)         # Telegram push
```

## Quick start

```bash
pip install -r requirements.txt
cp config.example.yaml config.yaml      # edit your keywords/location
cp .env.example .env                     # add Telegram bot token + chat id
python -m src.main
```

### Getting a Telegram bot token + chat id (automated)

1. In Telegram, message **@BotFather** → `/newbot` → copy the token.
2. Put the token in `.env` as `TELEGRAM_BOT_TOKEN=...`.
3. Send your new bot any message (e.g. "hi") so it's allowed to DM you.
4. Run the helper — it finds your chat id and sends a test push:

   ```bash
   python -m src.setup_telegram
   ```

   It prints the exact `TELEGRAM_CHAT_ID=...` line to paste into `.env`.

## Configuration (`config.yaml`)

```yaml
poll_interval_seconds: 300        # how often to poll. KEEP THIS HIGH.
posted_within: "r3600"            # LinkedIn time filter: r3600 = last hour
searches:
  - keywords: "python backend engineer"
    location: "Remote"
    include: ["python", "backend"]   # title/company must contain at least one
    exclude: ["senior", "lead"]      # skip if title contains any of these
  - keywords: "data analyst"
    location: "Bengaluru"
```

## Running it 24/7 (so alerts keep coming when your machine is off)

Running `python -m src.main` only works while that terminal is open. For
continuous alerts, pick one:

### Option A — Docker on an always-on host (best timing)

```bash
cp config.example.yaml config.yaml   # edit your searches
cp .env.example .env                  # add Telegram token + chat id
docker compose up -d --build
```
Runs the full poll loop forever, restarts on crash/reboot, and persists dedupe
state in `./data`. Use this if you have a VPS / Raspberry Pi / always-on box and
want the tightest polling interval.

### Option B — GitHub Actions cron (free, no server)

1. Push this repo to GitHub.
2. Repo **Settings → Secrets and variables → Actions** → add `TELEGRAM_BOT_TOKEN`
   and `TELEGRAM_CHAT_ID`.
3. Commit your `config.yaml` (it contains no secrets — just keywords).

`.github/workflows/job-alerts.yml` then polls on a schedule (default every
15 min) and pushes new matches. **Caveat:** GitHub's cron is best-effort, often
delayed several minutes, and 5 min is the floor — so latency is looser than
Option A. Fine for "I want jobs in my pocket," not for "the very newest second."

## Catching more jobs

The LinkedIn source paginates (newest-first) to pull more than the first page.
Tune it in `src/sources/linkedin_guest.py` via `max_pages` (default 4) and the
polite `page_delay` between page requests. Add more entries under `searches:` in
`config.yaml` to widen coverage — each is polled every interval.

## Try it without scraping

Set `source: mock` in `config.yaml` to run the full pipeline against a fake
feed — useful for testing your Telegram setup and matching rules offline.

## License / disclaimer

For personal, educational use. You are responsible for complying with
LinkedIn's terms. The authors accept no liability for misuse.
