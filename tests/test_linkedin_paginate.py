from src.models import Search
from src.sources.linkedin_guest import LinkedInGuestSource


def _card(job_id):
    return f"""
    <li>
      <div class="base-card" data-entity-urn="urn:li:jobPosting:{job_id}">
        <a class="base-card__full-link" href="https://www.linkedin.com/jobs/view/{job_id}">x</a>
        <h3 class="base-search-card__title">Engineer</h3>
        <h4 class="base-search-card__subtitle">Acme</h4>
      </div>
    </li>"""


def _page(ids):
    return "<ul>" + "".join(_card(i) for i in ids) + "</ul>"


def test_fetch_paginates_and_dedupes(monkeypatch):
    full = list(range(25))  # a full page triggers fetching the next one
    pages = iter([_page(full), _page([100, 101])])  # 2nd page is short -> stop
    src = LinkedInGuestSource(max_pages=4, page_delay=0)
    monkeypatch.setattr(src, "_get_with_backoff", lambda url: next(pages, None))

    jobs = src.fetch(Search(keywords="engineer"), "r3600")
    ids = [j.id for j in jobs]

    assert len(ids) == 27
    assert len(set(ids)) == 27  # no duplicates across pages


def test_fetch_stops_on_empty_page(monkeypatch):
    src = LinkedInGuestSource(max_pages=4, page_delay=0)
    monkeypatch.setattr(src, "_get_with_backoff", lambda url: "<ul></ul>")
    assert src.fetch(Search(keywords="x"), "r3600") == []
