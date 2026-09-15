import asyncio
import logging
import signal
import sys

import structlog

from worker.config import Config

log = structlog.get_logger()


def configure_logging(level: str) -> None:
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, level.upper(), logging.INFO),
    )
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.JSONRenderer(),
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
    )


async def process_one(item_id: int) -> None:
    """Placeholder for real work. Sleeps long enough that interrupting it
    mid-flight is observable."""
    log.info("processing", item_id=item_id)
    await asyncio.sleep(3)
    log.info("processed", item_id=item_id)


async def work_loop(cfg: Config, stop: asyncio.Event) -> None:
    """Polls for work until told to stop.

    The check happens BETWEEN items, never inside one. A job either runs to
    completion or does not start — no half-finished work.
    """
    counter = 0
    while not stop.is_set():
        counter += 1
        await process_one(counter)

        # Sleep, but wake immediately if a shutdown signal arrives.
        # A plain asyncio.sleep() would make shutdown wait out the full
        # interval before noticing.
        try:
            await asyncio.wait_for(stop.wait(), timeout=cfg.poll_interval)
        except asyncio.TimeoutError:
            pass

    log.info("work loop finished")


async def main() -> int:
    cfg = Config.load()
    configure_logging(cfg.log_level)

    stop = asyncio.Event()
    loop = asyncio.get_running_loop()

    # add_signal_handler, not signal.signal: the former integrates with the
    # event loop, the latter fires in a thread context where touching asyncio
    # objects is unsafe.
    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(
            sig, lambda s=sig: (log.info("signal received", signal=s.name), stop.set())
        )

    log.info("worker started", poll_interval=cfg.poll_interval)

    task = asyncio.create_task(work_loop(cfg, stop))

    await stop.wait()
    log.info("draining", timeout=cfg.shutdown_wait)

    # Give the current item time to finish. Unlike the API there is nothing
    # to drain from a socket — the question is only whether the in-flight job
    # completes.
    try:
        await asyncio.wait_for(task, timeout=cfg.shutdown_wait)
        log.info("stopped cleanly")
    except asyncio.TimeoutError:
        log.warning("drain timed out, cancelling in-flight work")
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))