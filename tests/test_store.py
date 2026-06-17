import tempfile
import os

from src.models import Job
from src.store import SeenStore


def _job(jid):
    return Job(id=jid, title="t", company="c", location="l", url="u")


def test_filter_new_and_mark_seen():
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    try:
        store = SeenStore(path)
        jobs = [_job("a"), _job("b")]

        assert {j.id for j in store.filter_new(jobs)} == {"a", "b"}

        store.mark_seen(jobs[0])
        assert {j.id for j in store.filter_new(jobs)} == {"b"}

        store.mark_seen(jobs[1])
        assert store.filter_new(jobs) == []
        store.close()
    finally:
        os.remove(path)


def test_seen_persists_across_instances():
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    try:
        s1 = SeenStore(path)
        s1.mark_seen(_job("x"))
        s1.close()

        s2 = SeenStore(path)
        assert s2.filter_new([_job("x"), _job("y")])[0].id == "y"
        s2.close()
    finally:
        os.remove(path)
