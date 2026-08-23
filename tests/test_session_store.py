"""Session metadata persistence tests."""

import json

import pytest

from scripts.session_store import atomic_write_json, resolve_fingerprint_seed


def test_generated_seed_is_persisted_and_reused(tmp_path):
    metadata_path = tmp_path / "session.json"

    first = resolve_fingerprint_seed(metadata_path, environ={})
    second = resolve_fingerprint_seed(metadata_path, environ={})
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))

    assert first == second
    assert metadata == {
        "version": 1,
        "seed": first,
        "saved_at": metadata["saved_at"],
    }
    assert metadata["saved_at"].endswith("Z")


def test_environment_seed_overrides_without_replacing_metadata(tmp_path):
    metadata_path = tmp_path / "session.json"
    persisted = resolve_fingerprint_seed(metadata_path, environ={})

    override = resolve_fingerprint_seed(
        metadata_path,
        environ={"XHS_FP_SEED": "process-only-seed"},
    )

    assert override == "process-only-seed"
    assert json.loads(metadata_path.read_text(encoding="utf-8"))["seed"] == persisted


def test_environment_seed_does_not_create_metadata(tmp_path):
    metadata_path = tmp_path / "session.json"

    resolved = resolve_fingerprint_seed(
        metadata_path,
        environ={"XHS_FP_SEED": "process-only-seed"},
    )

    assert resolved == "process-only-seed"
    assert not metadata_path.exists()


def test_corrupt_metadata_is_replaced_without_logging_seed(tmp_path, caplog):
    metadata_path = tmp_path / "session.json"
    leaked_seed = "do-not-log-this-seed"
    metadata_path.write_text(f'{{"seed": "{leaked_seed}"', encoding="utf-8")

    recovered = resolve_fingerprint_seed(metadata_path, environ={})
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))

    assert recovered == metadata["seed"]
    assert metadata["version"] == 1
    assert leaked_seed not in caplog.text
    assert recovered not in caplog.text


def test_atomic_write_failure_preserves_previous_file(tmp_path, monkeypatch):
    target = tmp_path / "session.json"
    target.write_text('{"old": true}\n', encoding="utf-8")

    def fail_replace(source, destination):
        raise OSError("replace failed")

    monkeypatch.setattr("scripts.session_store.os.replace", fail_replace)

    with pytest.raises(OSError, match="replace failed"):
        atomic_write_json(target, {"old": False})

    assert target.read_text(encoding="utf-8") == '{"old": true}\n'
    assert list(tmp_path.glob(".session.json.*.tmp")) == []
