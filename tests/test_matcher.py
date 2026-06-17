from src.matcher import matches
from src.models import Job, Search


def _job(title="Python Backend Engineer", company="Acme"):
    return Job(id="1", title=title, company=company, location="Remote", url="u")


def test_no_filters_matches_everything():
    assert matches(_job(), Search(keywords="x"))


def test_include_requires_one_term():
    s = Search(keywords="x", include=["python"])
    assert matches(_job(title="Python Dev"), s)
    assert not matches(_job(title="Java Dev"), s)


def test_exclude_rejects():
    s = Search(keywords="x", exclude=["senior"])
    assert not matches(_job(title="Senior Python Engineer"), s)
    assert matches(_job(title="Python Engineer"), s)


def test_exclude_takes_priority_over_include():
    s = Search(keywords="x", include=["python"], exclude=["lead"])
    assert not matches(_job(title="Lead Python Engineer"), s)


def test_matches_against_company_too():
    s = Search(keywords="x", include=["acme"])
    assert matches(_job(title="Engineer", company="Acme Corp"), s)
