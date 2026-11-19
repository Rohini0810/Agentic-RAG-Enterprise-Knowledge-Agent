#Function	Responsibility
#generate_request_id()	Creates a unique identifier for each question.
#log_event()	Records an event with metadata.
#track_duration()	Measures how long a pipeline stage takes.
#logger	Central application logger.
#One important concept: time.perf_counter()
#Unlike ordinary wall-clock time, perf_counter() is designed for measuring elapsed durations accurately. 
# We'll use it to measure retrieval and generation latency.
from textwrap import wrap
#track_duration() is a context manager, so we can wrap any operation:

import logging
import time
import uuid

from contextlib import contextmanager
from logging.handlers import RotatingFileHandler
from pathlib import Path


# Logging configuration
PROJECT_ROOT = Path(__file__).resolve().parent.parent
LOG_DIRECTORY = PROJECT_ROOT / "logs"
LOG_FILE = LOG_DIRECTORY / "agentic_rag.log"

MAX_LOG_SIZE = 1 * 1024 * 1024
BACKUP_COUNT = 5

LOG_DIRECTORY.mkdir(parents=True, exist_ok=True)

logger = logging.getLogger("agentic_rag")
logger.setLevel(logging.INFO)
logger.propagate = False

if not logger.handlers:

    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
    )

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    file_handler = RotatingFileHandler(
        LOG_FILE,
        maxBytes=MAX_LOG_SIZE,
        backupCount=BACKUP_COUNT,
        encoding="utf-8"
    )
    file_handler.setFormatter(formatter)

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)


def generate_request_id() -> str:
    """Generate a unique ID for each request."""
    return str(uuid.uuid4())


def log_event(
    event: str,
    request_id: str,
    level: str = "info",
    **metadata
):
    """Log an event with request context."""

    log_data = {
        "event": event,
        "request_id": request_id,
        **metadata
    }

    message = " | ".join(
        f"{key}={value}" for key, value in log_data.items()
    )

    log_method = getattr(logger, level.lower(), logger.info)
    log_method(message)


@contextmanager
def track_duration(
    event: str,
    request_id: str,
    **metadata
):
    """Measure execution time of a pipeline stage."""

    start_time = time.perf_counter()

    try:
        yield

    except Exception:
        duration_ms = round(
            (time.perf_counter() - start_time) * 1000, 2
        )

        log_event(
            event=f"{event}_failed",
            request_id=request_id,
            level="exception",
            duration_ms=duration_ms,
            status="failed",
            **metadata
        )
        raise

    else:
        duration_ms = round(
            (time.perf_counter() - start_time) * 1000, 2
        )

        log_event(
            event=f"{event}_completed",
            request_id=request_id,
            duration_ms=duration_ms,
            status="success",
            **metadata
        )
