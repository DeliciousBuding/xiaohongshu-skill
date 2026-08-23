"""Persistent, non-cookie session metadata helpers."""

from __future__ import annotations

import json
import os
import secrets
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

from ._logging import get_logger

log = get_logger(__name__)

SESSION_SCHEMA_VERSION = 1
FINGERPRINT_SEED_ENV = "XHS_FP_SEED"


def atomic_write_json(path: str | Path, value: Any) -> None:
    """Write JSON by replacing a temporary file in the same directory."""
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    fd, temp_name = tempfile.mkstemp(
        dir=target.parent,
        prefix=f".{target.name}.",
        suffix=".tmp",
    )
    temp_path = Path(temp_name)
    try:
        try:
            os.chmod(temp_path, 0o600)
        except OSError:
            pass
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(value, handle, ensure_ascii=False, indent=2)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temp_path, target)
    except Exception:
        try:
            os.close(fd)
        except OSError:
            pass
        try:
            temp_path.unlink()
        except OSError:
            pass
        raise


def _new_metadata(seed: str) -> dict[str, object]:
    return {
        "version": SESSION_SCHEMA_VERSION,
        "seed": seed,
        "saved_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
    }


def _metadata_seed(value: object) -> str | None:
    if not isinstance(value, dict):
        return None
    if value.get("version") != SESSION_SCHEMA_VERSION:
        return None
    seed = value.get("seed")
    if not isinstance(seed, str) or not seed.strip():
        return None
    if not isinstance(value.get("saved_at"), str):
        return None
    return seed


def resolve_fingerprint_seed(
    metadata_path: str | Path,
    environ: Mapping[str, str] | None = None,
) -> str:
    """Resolve a fingerprint seed without exposing it in logs.

    An environment override is process-local and does not replace persisted metadata.
    Otherwise a valid persisted seed is reused. Missing or invalid metadata is replaced
    atomically with a newly generated seed.
    """
    environment = os.environ if environ is None else environ
    override = environment.get(FINGERPRINT_SEED_ENV, "").strip()
    if override:
        return override

    path = Path(metadata_path)
    if path.exists():
        try:
            seed = _metadata_seed(json.loads(path.read_text(encoding="utf-8")))
        except (OSError, UnicodeError, json.JSONDecodeError):
            seed = None
        if seed is not None:
            return seed
        log.warning("Session metadata is invalid; generating replacement metadata")

    seed = secrets.token_hex(16)
    atomic_write_json(path, _new_metadata(seed))
    return seed
