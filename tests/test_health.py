import os
import time

from worker.health import beat


def test_beat_creates_and_refreshes(tmp_path):
    hb = tmp_path / "heartbeat"
    beat(hb)
    assert hb.exists()

    old = time.time() - 120
    os.utime(hb, (old, old))
    beat(hb)
    assert time.time() - hb.stat().st_mtime < 5
    