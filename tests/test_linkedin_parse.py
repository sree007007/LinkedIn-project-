from src.sources.linkedin_guest import LinkedInGuestSource

# A trimmed sample of the HTML the guest endpoint returns for one job card.
SAMPLE = """
<ul>
  <li>
    <div class="base-card" data-entity-urn="urn:li:jobPosting:3901234567">
      <a class="base-card__full-link" href="https://www.linkedin.com/jobs/view/python-engineer-at-acme-3901234567?refId=abc">link</a>
      <h3 class="base-search-card__title">Python Backend Engineer</h3>
      <h4 class="base-search-card__subtitle">Acme Corp</h4>
      <span class="job-search-card__location">Remote</span>
      <time datetime="2026-06-17">1 hour ago</time>
    </div>
  </li>
</ul>
"""


def test_parse_extracts_fields_and_id():
    jobs = LinkedInGuestSource._parse(SAMPLE)
    assert len(jobs) == 1
    job = jobs[0]
    assert job.id == "3901234567"
    assert job.title == "Python Backend Engineer"
    assert job.company == "Acme Corp"
    assert job.location == "Remote"
    assert job.url == "https://www.linkedin.com/jobs/view/python-engineer-at-acme-3901234567"
    assert job.source == "linkedin"


def test_parse_skips_cards_without_link_or_title():
    assert LinkedInGuestSource._parse("<ul><li><span>nope</span></li></ul>") == []
