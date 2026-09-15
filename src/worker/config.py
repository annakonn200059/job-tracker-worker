import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Config:
    database_url: str
    log_level: str
    shutdown_wait: float
    poll_interval: float

    @classmethod
    def load(cls) -> "Config":
        database_url = os.getenv("DATABASE_URL", "")
        if not database_url:
            raise ValueError("DATABASE_URL is required")

        return cls(
            database_url=database_url,
            log_level=os.getenv("LOG_LEVEL", "info"),
            shutdown_wait=float(os.getenv("SHUTDOWN_WAIT", "15")),
            poll_interval=float(os.getenv("POLL_INTERVAL", "5")),
        )
        
