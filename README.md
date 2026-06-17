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

### Getting a Telegram bot token + chat id

1. In Telegram, message **@BotFather** → `/newbot` → copy the token.
2. Message your new bot anything (so it can DM you).
3. Get your chat id: open
   `https://api.telegram.org/bot<TOKEN>/getUpdates` in a browser and read
   `result[].message.chat.id`.
4. Put both in `.env`.

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

## Try it without scraping

Set `source: mock` in `config.yaml` to run the full pipeline against a fake
feed — useful for testing your Telegram setup and matching rules offline.

## License / disclaimer

For personal, educational use. You are responsible for complying with
LinkedIn's terms. The authors accept no liability for misuse.
