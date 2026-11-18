
import io
import logging
import uuid

from logging.handlers import RotatingFileHandler

import pytest

from app.observability import (
    generate_request_id,
    log_event,
    track_duration,
    logger,
    LOG_FILE,
    MAX_LOG_SIZE,
    BACKUP_COUNT
)


def test_generate_request_id_returns_unique_uuid():
    request_id_1 = generate_request_id()
    request_id_2 = generate_request_id()

    assert uuid.UUID(request_id_1)
    assert uuid.UUID(request_id_2)
    assert request_id_1 != request_id_2


def test_log_event_writes_event_and_metadata():
    stream = io.StringIO()

    test_handler = logging.StreamHandler(stream)
    logger.addHandler(test_handler)

    try:
        log_event(
            event="test_event",
            request_id="test-123",
            status="success",
            strategy="single_query"
        )

        output = stream.getvalue()

        assert "test_event" in output
        assert "request_id=test-123" in output
        assert "status=success" in output
        assert "strategy=single_query" in output

    finally:
        logger.removeHandler(test_handler)
        test_handler.close()


def test_track_duration_logs_success():
    stream = io.StringIO()

    test_handler = logging.StreamHandler(stream)
    logger.addHandler(test_handler)

    try:
        with track_duration(
            event="test_retrieval",
            request_id="test-456"
        ):
            pass

        output = stream.getvalue()

        assert "test_retrieval_completed" in output
        assert "status=success" in output
        assert "duration_ms=" in output

    finally:
        logger.removeHandler(test_handler)
        test_handler.close()


def test_track_duration_logs_exception_and_reraises():
    stream = io.StringIO()

    test_handler = logging.StreamHandler(stream)
    logger.addHandler(test_handler)

    try:
        with pytest.raises(ValueError, match="Test failure"):
            with track_duration(
                event="test_generation",
                request_id="test-789"
            ):
                raise ValueError("Test failure")

        output = stream.getvalue()

        assert "test_generation_failed" in output
        assert "status=failed" in output
        assert "ValueError: Test failure" in output

    finally:
        logger.removeHandler(test_handler)
        test_handler.close()


def test_rotating_file_logging_configuration():
    file_handlers = [
        handler
        for handler in logger.handlers
        if isinstance(handler, RotatingFileHandler)
    ]

    assert file_handlers
    assert file_handlers[0].baseFilename.endswith(
        "agentic_rag.log"
    )
    assert file_handlers[0].maxBytes == MAX_LOG_SIZE
    assert file_handlers[0].backupCount == BACKUP_COUNT


def test_log_rotation_creates_backup_file(tmp_path):
    log_path = tmp_path / "rotation_test.log"

    handler = RotatingFileHandler(
        log_path,
        maxBytes=100,
        backupCount=2,
        encoding="utf-8"
    )

    test_logger = logging.getLogger("rotation_test")
    test_logger.setLevel(logging.INFO)
    test_logger.addHandler(handler)

    try:
        for index in range(10):
            test_logger.info(
                "Test log message %s with enough content to rotate",
                index
            )

        handler.flush()

        assert log_path.exists()
        assert (tmp_path / "rotation_test.log.1").exists()

    finally:
        test_logger.removeHandler(handler)
        handler.close()
