"""Entrypoint: wire config -> source -> notifier -> poller and run."""
from __future__ import annotations

import os
import sys

from .config import load_config
from .notifier import ConsoleNotifier, TelegramNotifier
from .poller import Poller
from .sources import get_source
from .store import SeenStore


def build_notifier(config):
    if config.telegram_ready:
        print("[main] using Telegram notifier")
        return TelegramNotifier(config.telegram_bot_token, config.telegram_chat_id)
    print(
        "[main] TELEGRAM_BOT_TOKEN/CHAT_ID not set — falling back to console output. "
        "See README to enable Telegram push."
    )
    return ConsoleNotifier()


def main() -> int:
    try:
        config = load_config()
    except (FileNotFoundError, ValueError) as exc:
        print(f"[main] config error: {exc}")
        return 1

    source = get_source(config.source)
    notifier = build_notifier(config)
    store = SeenStore(os.getenv("JOBS_DB_PATH", "jobs.db"))

    poller = Poller(config, source, notifier, store)

    once = "--once" in sys.argv
    try:
        if once:
            sent = poller.run_once()
            print(f"[main] single pass done; {sent} alert(s) sent")
        else:
            poller.run_forever()
    except KeyboardInterrupt:
        print("\n[main] stopped")
    finally:
        store.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
