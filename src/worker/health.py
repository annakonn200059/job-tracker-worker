from pathlib import Path

HEARTBEAT = Path("/tmp/heartbeat")


def beat(path: Path = HEARTBEAT) -> None:
    """Prove the work loop is still turning.

    The liveness probe checks this file's age. If the loop hangs, the file goes
    stale and Kubernetes restarts the pod.
    """
    path.touch()
