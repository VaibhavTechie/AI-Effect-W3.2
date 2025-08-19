# src/orchestrator/logging_config.py
import json
import logging
import os
import socket
import sys
import time
from typing import Tuple, Dict, Any


class JsonFormatter(logging.Formatter):
    """Emit one JSON object per log line (good for docker/k8s)."""
    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),  # UTC
            "level": record.levelname,
            "message": record.getMessage(),
            # common context fields used across the project:
            "service": getattr(record, "service", None),
            "container_id": getattr(record, "container_id", None),
            "node": getattr(record, "node", None),
            "task": getattr(record, "task", None),
            "status": getattr(record, "status", None),            # "start" | "success" | "failure"
            "duration_ms": getattr(record, "duration_ms", None),  # int
            "returncode": getattr(record, "returncode", None),    # int
            "trace_id": getattr(record, "trace_id", None),        # optional correlation id
        }
        # remove None values to keep logs clean
        return json.dumps({k: v for k, v in payload.items() if v is not None})


def _build_handlers(log_dir: str, log_file: str) -> Tuple[logging.Handler, logging.Handler]:
    os.makedirs(log_dir, exist_ok=True)
    formatter = JsonFormatter()

    sh = logging.StreamHandler(sys.stdout)
    sh.setFormatter(formatter)

    fh = logging.FileHandler(os.path.join(log_dir, log_file), encoding="utf-8")
    fh.setFormatter(formatter)

    return sh, fh


class ContextAdapter(logging.LoggerAdapter):
    """LoggerAdapter that *merges* adapter extras with call-time extras robustly."""
    def process(self, msg: str, kwargs: Dict[str, Any]):
        call_extra = kwargs.get("extra") or {}
        if not isinstance(call_extra, dict):
            call_extra = {"_extra_str": str(call_extra)}
        merged = dict(self.extra)   # adapter defaults (service, node)
        merged.update(call_extra)   # per-call extras win
        kwargs["extra"] = merged
        return msg, kwargs


def get_logger(service: str = "orchestrator") -> logging.LoggerAdapter:
    """
    Preferred API: returns a LoggerAdapter that automatically injects:
    - service (passed in)
    - node (from NODE_NAME env or machine hostname)
    Avoids double-adding handlers if called multiple times.
    """
    base = logging.getLogger(service)
    if not base.handlers:
        base.setLevel(os.getenv("LOG_LEVEL", "INFO").upper())

        log_dir = os.getenv("LOG_DIR", "logs")
        log_file = os.getenv("LOG_FILE", "execution_log.log")
        sh, fh = _build_handlers(log_dir, log_file)
        base.addHandler(sh)
        base.addHandler(fh)
        base.propagate = False

    node = os.getenv("NODE_NAME", socket.gethostname())
    # Use our ContextAdapter to guarantee merge of extras
    return ContextAdapter(base, {"service": service, "node": node})


def setup_logging(service: str = "orchestrator") -> logging.LoggerAdapter:
    """Backwards-compatible initializer."""
    return get_logger(service)
