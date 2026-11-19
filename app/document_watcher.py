
import logging
import threading
from pathlib import Path

from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

from app.config import DOCUMENTS_PATH
from app.ingestion import ingest_documents


logger = logging.getLogger(__name__)


class DocumentChangeHandler(FileSystemEventHandler):
    """Debounce document events and serialize ingestion."""

    def __init__(self, debounce_seconds: float = 2.0):
        self.debounce_seconds = debounce_seconds

        # Protect timer and shutdown state.
        self.state_lock = threading.Lock()

        # Ensure only one ingestion operation runs at a time.
        self.ingestion_lock = threading.Lock()

        self.timer = None
        self.stopping = False

    def on_any_event(self, event):
        if event.is_directory:
            return

        paths = [event.src_path]

        if getattr(event, "dest_path", None):
            paths.append(event.dest_path)

        # Only monitor TXT documents.
        if not any(
            Path(path).suffix.lower() == ".txt"
            for path in paths
        ):
            return

        with self.state_lock:
            if self.stopping:
                return

            logger.info(
                "Document change detected: %s",
                event.event_type
            )

            # Reset the timer when another event arrives.
            if self.timer is not None:
                self.timer.cancel()

            self.timer = threading.Timer(
                self.debounce_seconds,
                self._run_ingestion
            )

            self.timer.daemon = True
            self.timer.start()

    def _run_ingestion(self):
        with self.state_lock:
            if self.stopping:
                return

            self.timer = None

        # Serialize ingestion operations.
        with self.ingestion_lock:
            with self.state_lock:
                if self.stopping:
                    return

            try:
                logger.info(
                    "Starting automatic document synchronization"
                )

                result = ingest_documents()

                logger.info(
                    "Automatic document synchronization completed: %s",
                    result
                )

            except Exception:
                logger.exception(
                    "Automatic document synchronization failed"
                )

    def shutdown(self):
        """Cancel pending work and wait for active ingestion."""

        with self.state_lock:
            self.stopping = True

            if self.timer is not None:
                self.timer.cancel()
                self.timer = None

        # Wait for an ingestion already in progress to finish.
        with self.ingestion_lock:
            logger.info(
                "Document watcher handler shut down"
            )


def start_document_watcher():
    """Start monitoring the configured document directory."""

    documents_path = Path(DOCUMENTS_PATH)

    documents_path.mkdir(
        parents=True,
        exist_ok=True
    )

    handler = DocumentChangeHandler()

    observer = Observer()

    observer.schedule(
        handler,
        str(documents_path),
        recursive=False
    )

    observer.start()

    logger.info(
        "Document watcher started: %s",
        documents_path
    )

    return observer, handler
