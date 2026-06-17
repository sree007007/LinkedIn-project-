"""One-shot Telegram setup helper.

Run this after creating a bot with @BotFather and messaging it once:

    TELEGRAM_BOT_TOKEN=... python -m src.setup_telegram

It auto-discovers your chat id from recent messages to the bot, sends a test
push, and prints the exact line to paste into your .env file.
"""
from __future__ import annotations

import os
import sys

import requests
from dotenv import load_dotenv


def main() -> int:
    load_dotenv()
    token = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
    if not token:
        print(
            "TELEGRAM_BOT_TOKEN is not set.\n"
            "1) In Telegram, message @BotFather -> /newbot -> copy the token.\n"
            "2) Put it in .env as TELEGRAM_BOT_TOKEN=... (or export it).\n"
            "3) Send your new bot any message (say 'hi').\n"
            "4) Re-run this command."
        )
        return 1

    base = f"https://api.telegram.org/bot{token}"

    try:
        updates = requests.get(f"{base}/getUpdates", timeout=10).json()
    except requests.RequestException as exc:
        print(f"Could not reach Telegram: {exc}")
        return 1

    if not updates.get("ok"):
        print(f"Telegram rejected the token: {updates}")
        return 1

    chat_id = _latest_chat_id(updates.get("result", []))
    if chat_id is None:
        print(
            "No messages found. Open Telegram, send your bot any message "
            "(e.g. 'hi'), then run this again."
        )
        return 1

    # Send the confirmation push.
    resp = requests.post(
        f"{base}/sendMessage",
        json={
            "chat_id": chat_id,
            "text": "✅ LinkedIn Job Alerts is connected. You'll get job pushes here.",
        },
        timeout=10,
    ).json()

    if not resp.get("ok"):
        print(f"Found chat id {chat_id} but the test message failed: {resp}")
        return 1

    print(f"✅ Test message sent. Your chat id is: {chat_id}\n")
    print("Add this line to your .env file:")
    print(f"TELEGRAM_CHAT_ID={chat_id}")
    return 0


def _latest_chat_id(results: list) -> int | None:
    for update in reversed(results):
        msg = update.get("message") or update.get("channel_post") or {}
        chat = msg.get("chat") or {}
        if "id" in chat:
            return chat["id"]
    return None


if __name__ == "__main__":
    raise SystemExit(main())
