"""LinkedIn public 'guest' jobs source.

This hits the same unauthenticated endpoint that powers the job list shown to
logged-out visitors:

    https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search

No login or credentials are used. See README for the terms-of-service caveat:
this is public data, but automated access still goes against LinkedIn's User
Agreement, so poll respectfully and expect occasional rate-limiting.
"""
from __future__ import annotations

import time
from urllib.parse import urlencode

import requests
from bs4 import BeautifulSoup

from ..models import Job, Search
from .base import JobSource

_ENDPOINT = (
    "https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search"
)

# A single, honest, realistic browser UA. We do NOT rotate UAs / proxies to
# evade detection — that would cross into abuse. If blocked, slow down instead.
_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml",
    "Accept-Language": "en-US,en;q=0.9",
}


class LinkedInGuestSource(JobSource):
    name = "linkedin"

    def __init__(self, timeout: int = 15):
        self.timeout = timeout
        self._session = requests.Session()
        self._session.headers.update(_HEADERS)

    def fetch(self, search: Search, posted_within: str) -> list[Job]:
        params = {
            "keywords": search.keywords,
            "location": search.location,
            "f_TPR": posted_within,  # time-posted range, e.g. r3600 = last hour
            "sortBy": "DD",  # date descending -> newest first
            "start": 0,
        }
        url = f"{_ENDPOINT}?{urlencode(params)}"

        html = self._get_with_backoff(url)
        if html is None:
            return []

        return self._parse(html)

    def _get_with_backoff(self, url: str, attempts: int = 3) -> str | None:
        delay = 2
        for attempt in range(1, attempts + 1):
            try:
                resp = self._session.get(url, timeout=self.timeout)
            except requests.RequestException as exc:
                print(f"[linkedin] request error: {exc}")
                resp = None

            if resp is not None:
                if resp.status_code == 200:
                    return resp.text
                if resp.status_code == 429:
                    print(
                        "[linkedin] 429 rate-limited. Back off / increase "
                        "poll_interval_seconds."
                    )
                else:
                    print(f"[linkedin] HTTP {resp.status_code}")

            if attempt < attempts:
                time.sleep(delay)
                delay *= 2
        return None

    @staticmethod
    def _parse(html: str) -> list[Job]:
        soup = BeautifulSoup(html, "html.parser")
        jobs: list[Job] = []

        for card in soup.select("li"):
            link_el = card.select_one("a.base-card__full-link") or card.select_one(
                "a[href*='/jobs/view/']"
            )
            title_el = card.select_one(".base-search-card__title")
            company_el = card.select_one(".base-search-card__subtitle")
            location_el = card.select_one(".job-search-card__location")
            time_el = card.select_one("time")
            base_el = card.select_one("[data-entity-urn]")

            if not (link_el and title_el):
                continue

            url = (link_el.get("href") or "").split("?")[0].strip()
            job_id = _extract_job_id(base_el, url)
            if not job_id:
                continue

            jobs.append(
                Job(
                    id=job_id,
                    title=title_el.get_text(strip=True),
                    company=company_el.get_text(strip=True) if company_el else "",
                    location=location_el.get_text(strip=True) if location_el else "",
                    url=url,
                    posted_at=(time_el.get("datetime") if time_el else "") or "",
                    source="linkedin",
                )
            )

        return jobs


def _extract_job_id(base_el, url: str) -> str:
    """Prefer the urn:li:jobPosting id; fall back to the numeric id in the URL."""
    if base_el is not None:
        urn = base_el.get("data-entity-urn", "")
        if "jobPosting:" in urn:
            return urn.rsplit(":", 1)[-1]
    # .../jobs/view/<id>  or  .../jobs/view/some-title-<id>
    tail = url.rstrip("/").rsplit("/", 1)[-1]
    digits = "".join(ch for ch in tail if ch.isdigit())
    return digits
