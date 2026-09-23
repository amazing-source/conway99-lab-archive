#!/usr/bin/env python3
"""Offline structural validation for the Wave 34 status/design source audit."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
RESULTS = ROOT / "results.json"
MANIFEST = ROOT / "manifest.json"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> None:
    data = json.loads(RESULTS.read_text(encoding="utf-8"))

    assert data["claim_label"] == "CITED"
    assert data["overall_assessment"] == "PASS_WITH_BOUNDED_CAVEATS"

    resources = data["remote_resources"]
    assert len(resources) == 8
    assert len({item["id"] for item in resources}) == 8
    assert len({item["url"] for item in resources}) == 8
    for item in resources:
        assert item["http_status"] == 200
        assert item["response_body_bytes"] > 0
        assert len(item["response_body_sha256"]) == 64
        int(item["response_body_sha256"], 16)
        assert item["content_saved_locally"] is False

    by_id = {item["id"]: item for item in resources}
    assert by_id["B02"]["observed_text"].startswith("? 99 14 1 2")
    assert by_id["R03"]["matrix_link_count"] == 146
    assert by_id["R04"]["matrix_link_count"] == 590
    assert by_id["R03"]["numbering"]["complete_sequence"] is True
    assert by_id["R04"]["numbering"]["complete_sequence"] is True

    assessments = {item["id"]: item for item in data["claim_assessments"]}
    assert set(assessments) == {"C01", "C02", "C03"}
    assert assessments["C01"]["assessment"] == "CONFIRMED_MAINTAINED_STATUS"
    assert (
        assessments["C02"]["assessment"]
        == "CONFIRMED_CONTEXTUAL_APPROXIMATE_QUOTE"
    )
    assert (
        assessments["C03"]["assessment"]
        == "CONFIRMED_RESTRICTED_DERIVED_CORPUS"
    )
    assert all(item["claim_label"] == "CITED" for item in assessments.values())

    global_status = data["global_status"]
    assert global_status
    assert set(global_status.values()) == {"UNKNOWN"}

    policy = data["workspace_artifact_policy"]
    assert policy["remote_content_archived"] is False
    assert policy["vendored_third_party_pdfs"] == 0
    assert policy["vendored_third_party_archives"] == 0
    assert policy["vendored_third_party_matrices"] == 0

    if MANIFEST.exists():
        manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
        for record in manifest["files"]:
            path = ROOT / record["path"]
            assert path.is_file(), record["path"]
            assert path.stat().st_size == record["bytes"], record["path"]
            assert sha256(path) == record["sha256"], record["path"]

    print(
        "PASS: 8 remote metadata records, 3 bounded source assessments, "
        "all global research statuses UNKNOWN"
    )


if __name__ == "__main__":
    main()
