#!/usr/bin/env python3
"""Replay the frozen Wave 33 construction packages in their historical inputs.

The discovery and verifier packages were correctly frozen before the central
``STRUCTURE.md`` received its Wave 33 integration section.  Their original
input ledgers therefore must not be interpreted as assertions about mutable
central-document bytes in the later publication tree.

This module authenticates an immutable content-addressed snapshot of all eight
historical inputs, materializes a temporary synthetic repository, copies only
hash-accepted candidate/verifier bytes into it, and runs the unchanged 14
discovery tests plus the 36 verifier tests that do not require ignored local
solver binaries.  The solver-environment half of verifier test 08 is recorded
as NOT_REPLAYED_NONBLOCKING because the timeout is non-evidentiary.  Its
portable source-audit half and the frozen solver hash/version records are
checked independently.  Nothing is imported from the discovery package into
this module.
"""

from __future__ import annotations

import argparse
import ast
import base64
import hashlib
import importlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import zlib
from pathlib import Path, PurePosixPath
from typing import Any, Iterable


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
ARCHIVE = HERE / "historical-inputs.json"

HISTORICAL_STRUCTURE_SHA256 = (
    "45640fecaa5834b24063c682c7edd0898f2746253a7708a2c70c3610e4bcb99a"
)
EXPECTED_ARCHIVE_SHA256 = (
    "d62fc4311577d56cbf34f8bd4e63aefb3b796457b3d020f4322324073d82f7dd"
)

CANDIDATE_FREEZE = (
    REPO / "verification" / "wave33-rooted-construction-candidate-freeze.sha256"
)
CANDIDATE_FREEZE_SHA256 = (
    "441465c157f28e658afde31e6ca0cff49ccb5841a001150bd3e3af616c5bf63a"
)
CANDIDATE_ARTIFACT = (
    REPO / "attempts" / "wave33-rooted-construction" / "artifact-manifest.sha256"
)
CANDIDATE_ARTIFACT_SHA256 = (
    "0cd192c0182506b3c901806cc96abb9fe53f04dc906b0b5cd73bc9b602558ff4"
)
VERIFIER_DIR = REPO / "verification" / "wave33-rooted-construction"
VERIFIER_ARTIFACT = VERIFIER_DIR / "artifact-manifest.sha256"
VERIFIER_ARTIFACT_SHA256 = (
    "20c27560bdf9720cd1cf043b11c218130cd2891a2d3c874f9dbc9bce2f27fbbf"
)
PRECOMPARISON_MANIFEST_SHA256 = (
    "4ccbbad9c01eab764d9aa6fb207114e43f8c5a36bec3ec5bf0d161708ce0360d"
)

EXPECTED_EXACT_RESULTS_SHA256 = (
    "ba6640eacd041bc8349024a1d3f13e3d74bd67cdad64d2d78c9a94927319c496"
)
EXPECTED_COMPARISON_RESULTS_SHA256 = (
    "c0476fb877e0e7d6a6fc63b1a4c72bda0d7804a18a4e4b2b6d5a1bcbc4b6b459"
)
EXPECTED_COMPARISON_CLI_STDOUT_SHA256 = (
    "7025cc30551e219c224fe068d641a202db9f1c7a39e480908933e9a93fe597c5"
)
EXPECTED_CERTIFICATE_SHA256 = (
    "340e5df716ad63bceba25c745ab04c22ea1a3dca01e939072f09775a5fc5f634"
)
EXPECTED_EXACT_CHECKER_SHA256 = (
    "49fc20348a38e378f7e140cbbd7829dff54afe3caf0de3a2c54a82ca10981eec"
)
EXPECTED_SOLVER_INSPECTION_SHA256 = (
    "345e5976222b950b7bb9d3805f7cef0836cbbdff9e9abf2ec85454b28eada342"
)
EXPECTED_CANDIDATE_COMPARISON_SHA256 = (
    "c09e957131547f005f70c3b00d82644a0708653fcb51dbd8da78f5edf3660720"
)
EXPECTED_INDEPENDENT_CHECK_SHA256 = (
    "b494d6c93fe503ccdceb49015f71cd446b664165834c0289cb11986be0de1289"
)
EXPECTED_STATIC_SOURCE_AUDIT_SHA256 = (
    "d7f45c6931fe10062321f2349e2c64aec0806e3258f0fdc4368a837bf0c023f5"
)

HISTORICAL_INPUTS = {
    "AGENTS.md":
        "4d3e4590a8634cafaf5d87f288be211497f60a8f5ab40094a83f555724e469b3",
    "CONJECTURE.md":
        "7b4e67a28dbae58dffbf8f06a5fcb0241b12c34807dcb145ef2ff5c70d4c1c58",
    "STRUCTURE.md": HISTORICAL_STRUCTURE_SHA256,
    "agents/2026-07-24-wave32-rooted-proof.md":
        "04990231e3b42cded363e39ffea771556e52ec66fe03a97164ae99f40ddbefe0",
    "verification/wave32-rooted-vector/audit.md":
        "36d83232d82e30205e0aefa30aedff0a517de1edb0adbaa54575ea68d04ce1a5",
    "verification/wave32-rooted-vector/independent-results.json":
        "4ed239e997e4485abdab4e26a2e28e2a981b6fff069c4d926ccff3d2241dbe6f",
    "verification/wave32-rooted-vector/artifact-manifest.sha256":
        "2607c3000944e6d31ab5491a7d959ae4f97f05ac3e0d754baaf2830efcd085df",
    "verification/wave33-continuation-protocol.md":
        "b98b6bb8228b54b67cd949ee1bf6eb05ebd6ebe74f1cbc9e49b041a55e2d2fe6",
}

RECORDED_SOLVER_HASHES = {
    ".venv/Lib/site-packages/pysat/card.py":
        "adabf7fedfe60b36cbc3c48075770e87e3cd6c5b5a013552009ce96f282a890e",
    ".venv/Lib/site-packages/pysat/solvers.py":
        "253654d8efabae650a0d136ad2f2e6d30b57206b1fb70846c714197468a28f7e",
    ".venv/Lib/site-packages/pysolvers.cp313-win_amd64.pyd":
        "1019bacdbb9400cc54fa89aa39294fefe1c63d5a67fdab35f473364529ec72dd",
    ".venv/Lib/site-packages/scipy/optimize/_milp.py":
        "803785ebcc365d1c04967a267650953da01ed285ee8be1c7a66a9fe3dbf75c3c",
    ".venv/Lib/site-packages/scipy/optimize/_highspy/_core.cp313-win_amd64.pyd":
        "92d47727b06333f871f57427a6d9800481e3e9feeabd59d31320ded8028c5357",
    ".venv/Lib/site-packages/scipy/optimize/_highspy/"
    "_highs_options.cp313-win_amd64.pyd":
        "df51a5cdf24f3ff1f06f36ef25c88b0ea41c496f8f7e12bfd40ca840f56d30a5",
}

SOLVER_VERSION_LINES = {
    "python_sat": "python-sat 1.9.dev7",
    "cadical": "CaDiCaL 1.9.5 wrapper exposed as cadical195",
    "scipy_highs": "SciPy 1.18.0 MILP wrapper over bundled HiGHS",
}

EXACT_CHECKER_IMPORT_ROOTS = {
    "__future__",
    "argparse",
    "collections",
    "hashlib",
    "itertools",
    "json",
    "pathlib",
    "typing",
}

COMPARISON_IMPORT_ROOTS = {
    "__future__",
    "argparse",
    "ast",
    "collections",
    "hashlib",
    "independent_check",
    "itertools",
    "json",
    "math",
    "pathlib",
    "random",
    "re",
    "typing",
}

INDEPENDENT_CHECK_IMPORT_ROOTS = {
    "__future__",
    "argparse",
    "collections",
    "copy",
    "hashlib",
    "json",
    "math",
    "pathlib",
    "typing",
}

OMITTED_VERIFIER_TEST = (
    "test_candidate_comparison.CandidateComparisonTests."
    "test_08_source_and_solver_provenance"
)

FULL_VERIFIER_TEST_IDS_SHA256 = (
    "ab8dea45aa3a32d4df0758dd9fe142c2fa6fecb815693085027e17313202d9e1"
)
INCLUDED_VERIFIER_TEST_IDS_SHA256 = (
    "185da0159a5f9689b2a60a830d9c78be9ea0d7c14c3535dd9ce992dc69542389"
)
DISCOVERY_TEST_IDS_SHA256 = (
    "1c8b91a4ee799f4c0cb336bc48ffd4a2f2b010a0860a53157dd6adae33adc784"
)

MANIFEST_LINE = re.compile(r"^([0-9a-f]{64})  (.+)$")
WAVE33_STRUCTURE_START = (
    b"## Wave 33 finite rooted extension and rootless contraction wall\n"
)
POST_WAVE33_STRUCTURE_MARKER = b"Each of the two central diagonal nonedges"


class ChronologyError(RuntimeError):
    """Raised when a frozen chronology or isolated replay gate fails."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ChronologyError(message)


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_path(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def canonical_json_bytes(value: Any) -> bytes:
    return (
        json.dumps(value, indent=2, sort_keys=True, ensure_ascii=True)
        .encode("utf-8")
        + b"\n"
    )


def reject_duplicate_json_pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    value: dict[str, Any] = {}
    for key, item in pairs:
        require(key not in value, f"duplicate JSON key: {key}")
        value[key] = item
    return value


def safe_repo_relative(raw: str) -> PurePosixPath:
    require("\\" not in raw, f"manifest path must use forward slashes: {raw}")
    relative = PurePosixPath(raw)
    require(not relative.is_absolute(), f"absolute manifest path: {raw}")
    require(
        relative.parts
        and all(part not in ("", ".", "..") for part in relative.parts),
        f"escaping or empty manifest path: {raw}",
    )
    return relative


def parse_manifest_bytes(
    data: bytes,
    *,
    label: str,
    expected_sha256: str | None = None,
) -> dict[str, str]:
    if expected_sha256 is not None:
        require(
            sha256_bytes(data) == expected_sha256,
            f"{label}: manifest byte hash mismatch",
        )
    require(data.endswith(b"\n"), f"{label}: missing terminal LF")
    require(b"\r" not in data and b"\0" not in data, f"{label}: invalid bytes")
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ChronologyError(f"{label}: invalid UTF-8") from exc
    entries: dict[str, str] = {}
    for line_number, line in enumerate(text.splitlines(), start=1):
        match = MANIFEST_LINE.fullmatch(line)
        require(match is not None, f"{label}: malformed line {line_number}")
        expected, raw = match.groups()
        safe_repo_relative(raw)
        require(raw not in entries, f"{label}: duplicate path: {raw}")
        entries[raw] = expected
    require(entries, f"{label}: empty manifest")
    return entries


def require_regular_source(path: Path, *, label: str) -> None:
    require(path.exists(), f"{label}: missing file")
    require(path.is_file(), f"{label}: not a regular file")
    require(not path.is_symlink(), f"{label}: symlink is forbidden")


def validate_manifest(
    path: Path,
    *,
    base: Path,
    expected_sha256: str,
) -> dict[str, str]:
    require_regular_source(path, label=str(path))
    entries = parse_manifest_bytes(
        path.read_bytes(), label=str(path), expected_sha256=expected_sha256
    )
    base_resolved = base.resolve()
    for raw, expected in entries.items():
        relative = safe_repo_relative(raw)
        target = base.joinpath(*relative.parts)
        require_regular_source(target, label=f"{path}:{raw}")
        resolved = target.resolve()
        require(
            resolved == base_resolved or base_resolved in resolved.parents,
            f"{path}: resolved path escapes base: {raw}",
        )
        require(
            sha256_path(target) == expected,
            f"{path}: entry hash mismatch: {raw}",
        )
    return entries


def historical_structure_bytes(current: bytes) -> bytes:
    if sha256_bytes(current) == HISTORICAL_STRUCTURE_SHA256:
        return current
    require(
        WAVE33_STRUCTURE_START in current,
        "integrated STRUCTURE.md lacks the Wave 33 insertion marker",
    )
    start = current.index(WAVE33_STRUCTURE_START)
    require(
        POST_WAVE33_STRUCTURE_MARKER in current[start:],
        "integrated STRUCTURE.md lacks the post-insertion marker",
    )
    end = current.index(POST_WAVE33_STRUCTURE_MARKER, start)
    recovered = current[:start] + current[end:]
    require(
        sha256_bytes(recovered) == HISTORICAL_STRUCTURE_SHA256,
        "recovered historical STRUCTURE.md hash mismatch",
    )
    return recovered


def build_archive_payload(source_root: Path = REPO) -> dict[str, Any]:
    entries: list[dict[str, Any]] = []
    for relative, expected in sorted(HISTORICAL_INPUTS.items()):
        source = source_root / relative
        require_regular_source(source, label=f"archive source {relative}")
        data = source.read_bytes()
        if relative == "STRUCTURE.md":
            data = historical_structure_bytes(data)
        require(
            sha256_bytes(data) == expected,
            f"archive source hash mismatch: {relative}",
        )
        compressed = zlib.compress(data, level=9)
        entries.append(
            {
                "path": relative,
                "sha256": expected,
                "size": len(data),
                "encoding": "zlib+base85",
                "payload": base64.b85encode(compressed).decode("ascii"),
            }
        )
    return {
        "schema_version": 1,
        "evidence_kind": "IMMUTABLE_HISTORICAL_INPUT_SNAPSHOT",
        "scope": (
            "The eight exact inputs named by the frozen construction input "
            "ledger and continuation addendum; no current central bytes."
        ),
        "entries": entries,
    }


def decode_archive_bytes(
    raw: bytes,
    *,
    expected_archive_sha256: str | None = EXPECTED_ARCHIVE_SHA256,
) -> dict[str, bytes]:
    if expected_archive_sha256 is not None:
        require(
            sha256_bytes(raw) == expected_archive_sha256,
            "historical archive byte hash mismatch",
        )
    try:
        value = json.loads(raw, object_pairs_hook=reject_duplicate_json_pairs)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ChronologyError("historical archive is not strict JSON") from exc
    require(isinstance(value, dict), "archive must be an object")
    require(
        set(value) == {"schema_version", "evidence_kind", "scope", "entries"},
        "archive top-level schema drift",
    )
    require(value["schema_version"] == 1, "archive schema_version drift")
    require(
        value["evidence_kind"] == "IMMUTABLE_HISTORICAL_INPUT_SNAPSHOT",
        "archive evidence_kind drift",
    )
    rows = value["entries"]
    require(isinstance(rows, list), "archive entries must be a list")
    decoded: dict[str, bytes] = {}
    for index, row in enumerate(rows):
        require(isinstance(row, dict), f"archive entry {index} must be an object")
        require(
            set(row) == {"path", "sha256", "size", "encoding", "payload"},
            f"archive entry {index} schema drift",
        )
        path = row["path"]
        require(isinstance(path, str), f"archive entry {index} path type")
        safe_repo_relative(path)
        require(path not in decoded, f"archive duplicate path: {path}")
        require(row["encoding"] == "zlib+base85", f"archive codec drift: {path}")
        require(
            isinstance(row["sha256"], str)
            and re.fullmatch(r"[0-9a-f]{64}", row["sha256"]) is not None,
            f"archive hash syntax: {path}",
        )
        require(
            isinstance(row["size"], int)
            and not isinstance(row["size"], bool)
            and row["size"] >= 0,
            f"archive size type: {path}",
        )
        require(isinstance(row["payload"], str), f"archive payload type: {path}")
        try:
            data = zlib.decompress(base64.b85decode(row["payload"].encode("ascii")))
        except (UnicodeEncodeError, ValueError, zlib.error) as exc:
            raise ChronologyError(f"archive payload decode failed: {path}") from exc
        require(len(data) == row["size"], f"archive size mismatch: {path}")
        require(
            sha256_bytes(data) == row["sha256"],
            f"archive entry hash mismatch: {path}",
        )
        decoded[path] = data
    require(
        {path: sha256_bytes(data) for path, data in decoded.items()}
        == HISTORICAL_INPUTS,
        "archive path/hash map differs from frozen input ledgers",
    )
    return decoded


def write_exact(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)


def copy_hash_accepted(
    source: Path,
    destination: Path,
    *,
    expected_sha256: str,
    label: str,
) -> None:
    require_regular_source(source, label=label)
    require(sha256_path(source) == expected_sha256, f"{label}: hash mismatch")
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source, destination, follow_symlinks=False)
    require(
        sha256_path(destination) == expected_sha256,
        f"{label}: copied-byte hash mismatch",
    )


def validate_frozen_packages(source_root: Path = REPO) -> dict[str, Any]:
    candidate_freeze = (
        source_root
        / "verification"
        / "wave33-rooted-construction-candidate-freeze.sha256"
    )
    candidate_artifact = (
        source_root
        / "attempts"
        / "wave33-rooted-construction"
        / "artifact-manifest.sha256"
    )
    verifier_dir = (
        source_root / "verification" / "wave33-rooted-construction"
    )
    verifier_artifact = verifier_dir / "artifact-manifest.sha256"

    candidate_entries = validate_manifest(
        candidate_freeze,
        base=source_root,
        expected_sha256=CANDIDATE_FREEZE_SHA256,
    )
    require(len(candidate_entries) == 17, "candidate freeze entry count drift")
    candidate_artifact_entries = validate_manifest(
        candidate_artifact,
        base=source_root,
        expected_sha256=CANDIDATE_ARTIFACT_SHA256,
    )
    require(
        len(candidate_artifact_entries) == 16,
        "candidate artifact entry count drift",
    )
    nested = dict(candidate_entries)
    nested_manifest_hash = nested.pop(
        "attempts/wave33-rooted-construction/artifact-manifest.sha256",
        None,
    )
    require(
        nested_manifest_hash == CANDIDATE_ARTIFACT_SHA256,
        "candidate freeze does not bind the nested artifact manifest",
    )
    require(
        nested == candidate_artifact_entries,
        "candidate freeze and artifact entries disagree",
    )

    verifier_entries = validate_manifest(
        verifier_artifact,
        base=verifier_dir,
        expected_sha256=VERIFIER_ARTIFACT_SHA256,
    )
    require(len(verifier_entries) == 14, "verifier artifact entry count drift")
    precomparison = verifier_dir / "precomparison-freeze.sha256"
    precomparison_entries = validate_manifest(
        precomparison,
        base=verifier_dir,
        expected_sha256=PRECOMPARISON_MANIFEST_SHA256,
    )
    require(
        len(precomparison_entries) == 5,
        "precomparison manifest entry count drift",
    )
    return {
        "candidate_entries": candidate_entries,
        "candidate_artifact_entries": candidate_artifact_entries,
        "verifier_entries": verifier_entries,
        "precomparison_entries": precomparison_entries,
    }


def audit_import_roots(
    path: Path,
    *,
    expected_sha256: str,
    expected_roots: set[str],
    label: str,
) -> dict[str, Any]:
    require_regular_source(path, label=label)
    require(sha256_path(path) == expected_sha256, f"{label}: hash mismatch")
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"))
    except (UnicodeDecodeError, SyntaxError) as exc:
        raise ChronologyError(f"{label}: source parse failed") from exc
    imported_roots: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported_roots.update(
                alias.name.split(".", 1)[0] for alias in node.names
            )
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported_roots.add(node.module.split(".", 1)[0])
    require(
        imported_roots == expected_roots,
        f"{label}: import-root set drift",
    )
    return {
        "source_sha256": expected_sha256,
        "import_roots": sorted(imported_roots),
        "status": "PASS",
    }


def audit_exact_checker_standard_library(exact_path: Path) -> dict[str, Any]:
    result = audit_import_roots(
        exact_path,
        expected_sha256=EXPECTED_EXACT_CHECKER_SHA256,
        expected_roots=EXACT_CHECKER_IMPORT_ROOTS,
        label="exact checker",
    )
    result["standard_library_only"] = True
    return result


def validate_solver_inspection_records(path: Path) -> dict[str, Any]:
    require_regular_source(path, label="solver inspection record")
    require(
        sha256_path(path) == EXPECTED_SOLVER_INSPECTION_SHA256,
        "solver inspection record hash mismatch",
    )
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError as exc:
        raise ChronologyError("solver inspection record is not UTF-8") from exc
    for label, line in SOLVER_VERSION_LINES.items():
        require(
            text.count(line) == 1,
            f"solver inspection version record drift: {label}",
        )
    observed: dict[str, str] = {}
    for match in re.finditer(
        r"(?m)^([0-9a-f]{64})  (\.venv/[^\r\n]+)$",
        text,
    ):
        digest, relative = match.groups()
        require(
            relative not in observed,
            f"duplicate solver inspection hash record: {relative}",
        )
        observed[relative] = digest
    require(
        observed == RECORDED_SOLVER_HASHES,
        "solver inspection path/hash records drift",
    )
    for phrase in (
        "Its exit status is not a certificate.",
        "uses only the Python",
        "standard library. No solver nonhit or UNSAT response will be promoted.",
    ):
        require(phrase in text, f"solver inspection status wall missing: {phrase}")
    return {
        "document_sha256": EXPECTED_SOLVER_INSPECTION_SHA256,
        "documentary_hash_record_count": len(observed),
        "documentary_hash_records": observed,
        "version_record_count": len(SOLVER_VERSION_LINES),
        "version_records": SOLVER_VERSION_LINES,
        "observed_environment_hash_count": 0,
        "local_environment_files_opened": 0,
        "status": "AUTHENTICATED_RECORDS_ONLY",
    }


def run_chronology_owned_comparison(root: Path) -> dict[str, Any]:
    verifier_dir = root / "verification" / "wave33-rooted-construction"
    attempt_dir = root / "attempts" / "wave33-rooted-construction"
    comparison_path = verifier_dir / "candidate_comparison.py"
    independent_path = verifier_dir / "independent_check.py"
    comparison_imports = audit_import_roots(
        comparison_path,
        expected_sha256=EXPECTED_CANDIDATE_COMPARISON_SHA256,
        expected_roots=COMPARISON_IMPORT_ROOTS,
        label="candidate comparison",
    )
    independent_imports = audit_import_roots(
        independent_path,
        expected_sha256=EXPECTED_INDEPENDENT_CHECK_SHA256,
        expected_roots=INDEPENDENT_CHECK_IMPORT_ROOTS,
        label="independent checker",
    )
    exact_imports = audit_exact_checker_standard_library(
        attempt_dir / "exact_check.py"
    )
    solver_records = validate_solver_inspection_records(
        attempt_dir / "solver-inspection.md"
    )

    module_names = ("candidate_comparison", "independent_check")
    saved_modules = {
        name: sys.modules[name] for name in module_names if name in sys.modules
    }
    old_path = list(sys.path)
    old_dont_write_bytecode = sys.dont_write_bytecode
    try:
        sys.dont_write_bytecode = True
        sys.path.insert(0, str(verifier_dir))
        for name in module_names:
            sys.modules.pop(name, None)
        pre = importlib.import_module("independent_check")
        comparison = importlib.import_module("candidate_comparison")
        require(
            Path(pre.__file__).resolve() == independent_path.resolve(),
            "independent checker import escaped the synthetic root",
        )
        require(
            Path(comparison.__file__).resolve() == comparison_path.resolve(),
            "candidate comparison import escaped the synthetic root",
        )

        manifests = comparison.verify_manifests()
        certificate_path = attempt_dir / "partial-design-certificate.json"
        certificate = pre.load_json(certificate_path)
        parsed = comparison.parse_certificate(certificate)
        bounded = pre.load_json(attempt_dir / "bounded-search-manifest.json")
        normalized = comparison.normalized_payload(parsed, bounded)
        frozen_check = pre.verify_payload(
            normalized,
            input_sha256=pre.sha256_path(certificate_path),
        )
        bf = comparison.direct_bf_metrics(parsed)
        encoding = comparison.independent_assignment_encoding(parsed)
        milp = comparison.verify_bounded_manifest(bounded, encoding)
        exact_results = pre.load_json(attempt_dir / "exact-results.json")
        base_results = pre.load_json(attempt_dir / "base-results.json")
        recorded = comparison.verify_recorded_results(
            exact_results,
            base_results,
            bf,
        )
        source_audit = comparison.static_source_audit()
        require(
            sha256_bytes(canonical_json_bytes(source_audit))
            == EXPECTED_STATIC_SOURCE_AUDIT_SHA256,
            "portable source-audit result drift",
        )
        require(
            source_audit["exact_checker_standard_library_only"] is True,
            "portable source audit did not accept exact checker imports",
        )
        scope_documents = comparison.static_scope_documents()
        hostile_search = comparison.reproduce_hostile_search(parsed)
        accepted_path = verifier_dir / "candidate-comparison-results.json"
        require(
            sha256_path(accepted_path) == EXPECTED_COMPARISON_RESULTS_SHA256,
            "accepted comparison result hash drift",
        )
        accepted = pre.load_json(accepted_path)
        assert_status_wall(accepted)
        require(accepted["claim_label"] == "VERIFIED", "accepted claim drift")
        require(
            accepted["assignment_encoding"]["row_system_sha256"]
            == encoding["row_system_sha256"],
            "accepted assignment-row digest is not core-bound",
        )
        for observed_key, accepted_key in (
            ("violation_count", "BF_violation_count"),
            ("squared_defect", "BF_squared_defect"),
            ("exact_support_group_count", "BF_exact_support_group_count"),
        ):
            require(
                bf[observed_key] == accepted["hostile_partial"][accepted_key],
                f"accepted hostile BF summary drift: {observed_key}",
            )
        require(
            hostile_search["certificate_sha256"] == EXPECTED_CERTIFICATE_SHA256,
            "hostile-search certificate hash drift",
        )
        require(
            hostile_search["byte_identical"] is True,
            "hostile-search certificate is not byte-identical",
        )

        projection = {
            "schema_version": 1,
            "execution_mode": (
                "CHRONOLOGY_OWNED_CALLS_TO_HASH_PINNED_COMPARISON_FUNCTIONS"
            ),
            "unchanged_candidate_comparison_cli": "NOT_RUN_BY_DESIGN",
            "functions_called": [
                "verify_manifests",
                "parse_certificate",
                "normalized_payload",
                "independent_check.verify_payload",
                "direct_bf_metrics",
                "independent_assignment_encoding",
                "verify_bounded_manifest",
                "verify_recorded_results",
                "static_source_audit",
                "static_scope_documents",
                "reproduce_hostile_search",
            ],
            "candidate_comparison_import_audit": comparison_imports,
            "independent_check_import_audit": independent_imports,
            "exact_checker_import_audit": exact_imports,
            "solver_inspection_records": solver_records,
            "manifests": manifests,
            "frozen_check": {
                "BF_violation_count": frozen_check["hostile_partial"]["BF"][
                    "violation_count"
                ],
                "BF_squared_defect": frozen_check["hostile_partial"]["BF"][
                    "squared_defect"
                ],
                "O_O_layer_certificate_status": frozen_check["hostile_partial"][
                    "O_O_layer_certificate_status"
                ],
            },
            "BF": bf,
            "assignment_encoding": encoding,
            "milp_run": milp,
            "recorded_results": recorded,
            "static_source_audit": source_audit,
            "scope_documents": scope_documents,
            "hostile_search": hostile_search,
            "accepted_summary_sha256": EXPECTED_COMPARISON_RESULTS_SHA256,
            "accepted_summary_core_bound": True,
        }
        return projection
    finally:
        sys.path[:] = old_path
        sys.dont_write_bytecode = old_dont_write_bytecode
        for name in module_names:
            sys.modules.pop(name, None)
        sys.modules.update(saved_modules)


def materialize_historical_root(
    destination: Path,
    *,
    source_root: Path = REPO,
    archive_path: Path = ARCHIVE,
) -> dict[str, Any]:
    require(not destination.exists(), "synthetic root must not already exist")
    destination.mkdir(parents=True)
    archive_bytes = archive_path.read_bytes()
    historical = decode_archive_bytes(archive_bytes)
    frozen = validate_frozen_packages(source_root)

    for relative, data in historical.items():
        write_exact(destination.joinpath(*PurePosixPath(relative).parts), data)

    for relative, expected in frozen["candidate_entries"].items():
        source = source_root.joinpath(*PurePosixPath(relative).parts)
        target = destination.joinpath(*PurePosixPath(relative).parts)
        copy_hash_accepted(
            source, target, expected_sha256=expected, label=f"candidate {relative}"
        )

    verifier_source = (
        source_root / "verification" / "wave33-rooted-construction"
    )
    verifier_destination = (
        destination / "verification" / "wave33-rooted-construction"
    )
    for relative, expected in frozen["verifier_entries"].items():
        copy_hash_accepted(
            verifier_source.joinpath(*PurePosixPath(relative).parts),
            verifier_destination.joinpath(*PurePosixPath(relative).parts),
            expected_sha256=expected,
            label=f"verifier {relative}",
        )

    copy_hash_accepted(
        source_root
        / "verification"
        / "wave33-rooted-construction-candidate-freeze.sha256",
        destination
        / "verification"
        / "wave33-rooted-construction-candidate-freeze.sha256",
        expected_sha256=CANDIDATE_FREEZE_SHA256,
        label="candidate freeze",
    )

    require(
        sha256_path(destination / "STRUCTURE.md")
        == HISTORICAL_STRUCTURE_SHA256,
        "synthetic root did not receive historical STRUCTURE.md",
    )
    exact_imports = audit_exact_checker_standard_library(
        destination
        / "attempts"
        / "wave33-rooted-construction"
        / "exact_check.py"
    )
    solver_records = validate_solver_inspection_records(
        destination
        / "attempts"
        / "wave33-rooted-construction"
        / "solver-inspection.md"
    )
    require(
        not (destination / ".venv").exists(),
        "synthetic root unexpectedly contains a local solver environment",
    )
    return {
        "historical_input_count": len(historical),
        "candidate_freeze_entries": len(frozen["candidate_entries"]),
        "candidate_artifact_entries": len(frozen["candidate_artifact_entries"]),
        "verifier_artifact_entries": len(frozen["verifier_entries"]),
        "precomparison_entries": len(frozen["precomparison_entries"]),
        "solver_provenance_files_copied": 0,
        "solver_hash_records_authenticated":
            solver_records["documentary_hash_record_count"],
        "solver_version_records_authenticated":
            solver_records["version_record_count"],
        "exact_checker_standard_library_only":
            exact_imports["standard_library_only"],
        "local_environment_dependency": False,
    }


def tree_snapshot(root: Path) -> dict[str, str]:
    snapshot: dict[str, str] = {}
    for path in sorted(root.rglob("*")):
        if path.is_file():
            relative = path.relative_to(root).as_posix()
            snapshot[relative] = sha256_path(path)
    return snapshot


def run_process(
    command: list[str],
    *,
    cwd: Path,
    environment: dict[str, str],
) -> subprocess.CompletedProcess[bytes]:
    completed = subprocess.run(
        command,
        cwd=cwd,
        env=environment,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if completed.returncode != 0:
        stdout = completed.stdout.decode("utf-8", errors="replace")[-2000:]
        stderr = completed.stderr.decode("utf-8", errors="replace")[-4000:]
        raise ChronologyError(
            f"subprocess failed ({completed.returncode}): {command}\n"
            f"stdout tail:\n{stdout}\nstderr tail:\n{stderr}"
        )
    return completed


def unittest_count(completed: subprocess.CompletedProcess[bytes]) -> int:
    combined = completed.stdout + b"\n" + completed.stderr
    matches = re.findall(rb"Ran ([0-9]+) tests?", combined)
    require(len(matches) == 1, "could not determine exact unittest count")
    return int(matches[0])


def isolated_subprocess_environment() -> dict[str, str]:
    environment = os.environ.copy()
    for key in tuple(environment):
        upper = key.upper()
        if (
            upper.startswith("PYTHON")
            or upper.startswith("CONDA")
            or upper in {"VIRTUAL_ENV", "VIRTUAL_ENV_PROMPT"}
        ):
            environment.pop(key, None)
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    return environment


def complete_suite_runner_source(
    *,
    expected_count: int,
    expected_ids_sha256: str,
) -> str:
    return f"""
import hashlib
import json
import sys
import unittest

start_dir = sys.argv[1]
sys.path.insert(0, start_dir)

def flatten(suite):
    for item in suite:
        if isinstance(item, unittest.TestSuite):
            yield from flatten(item)
        else:
            yield item

loader = unittest.TestLoader()
discovered = loader.discover(
    start_dir=start_dir,
    pattern="test_*.py",
    top_level_dir=start_dir,
)
tests = list(flatten(discovered))
tests.sort(key=lambda test: test.id())
ids = [test.id() for test in tests]
ids_sha256 = hashlib.sha256(
    "".join(value + "\\n" for value in ids).encode("utf-8")
).hexdigest()
if len(ids) != {expected_count!r}:
    raise SystemExit("test count drift: " + str(len(ids)))
if ids_sha256 != {expected_ids_sha256!r}:
    raise SystemExit("test-ID digest drift")
result = unittest.TextTestRunner(verbosity=1).run(
    unittest.TestSuite(tests)
)
print(json.dumps({{
    "test_count": len(ids),
    "test_ids_sha256": ids_sha256,
}}, sort_keys=True))
raise SystemExit(0 if result.wasSuccessful() else 1)
""".lstrip()


def filtered_verifier_runner_source() -> str:
    return f"""
import hashlib
import json
import sys
import unittest

start_dir = sys.argv[1]
sys.path.insert(0, start_dir)

def flatten(suite):
    for item in suite:
        if isinstance(item, unittest.TestSuite):
            yield from flatten(item)
        else:
            yield item

loader = unittest.TestLoader()
discovered = loader.discover(
    start_dir=start_dir,
    pattern="test_*.py",
    top_level_dir=start_dir,
)
tests = list(flatten(discovered))
tests.sort(key=lambda test: test.id())
ids = [test.id() for test in tests]
digest = lambda values: hashlib.sha256(
    "".join(value + "\\n" for value in values).encode("utf-8")
).hexdigest()
if len(ids) != 37:
    raise SystemExit("full verifier test count drift: " + str(len(ids)))
if digest(ids) != {FULL_VERIFIER_TEST_IDS_SHA256!r}:
    raise SystemExit("full verifier test-ID digest drift")
if ids.count({OMITTED_VERIFIER_TEST!r}) != 1:
    raise SystemExit("designated verifier test missing or duplicated")
selected = [
    test for test in tests if test.id() != {OMITTED_VERIFIER_TEST!r}
]
selected_ids = [test.id() for test in selected]
if len(selected_ids) != 36:
    raise SystemExit("selected verifier test count drift")
if digest(selected_ids) != {INCLUDED_VERIFIER_TEST_IDS_SHA256!r}:
    raise SystemExit("selected verifier test-ID digest drift")
result = unittest.TextTestRunner(verbosity=1).run(
    unittest.TestSuite(selected)
)
print(json.dumps({{
    "full_test_count": len(ids),
    "full_test_ids_sha256": digest(ids),
    "omitted_test_id": {OMITTED_VERIFIER_TEST!r},
    "selected_test_count": len(selected_ids),
    "selected_test_ids_sha256": digest(selected_ids),
}}, sort_keys=True))
raise SystemExit(0 if result.wasSuccessful() else 1)
""".lstrip()


def runner_metadata(
    completed: subprocess.CompletedProcess[bytes],
) -> dict[str, Any]:
    try:
        value = json.loads(completed.stdout)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ChronologyError("test runner did not emit strict JSON metadata") from exc
    require(isinstance(value, dict), "test runner metadata must be an object")
    return value


def assert_status_wall(payload: Any) -> None:
    require(isinstance(payload, dict), "comparison result must be an object")
    wall = payload.get("status_wall")
    require(isinstance(wall, dict), "comparison status wall missing")
    expected = {
        "complete_graph_extension": "UNKNOWN",
        "complete_domain_UNSAT_certificate": "NONE",
        "full_rooted_endpoint": "UNKNOWN",
        "n3_708": "UNKNOWN",
        "Conway_99": "UNKNOWN",
        "novelty": "UNKNOWN",
        "timeout_negative_evidence": False,
    }
    require(wall == expected, "comparison status wall drift or promotion")


def assert_clean_clone_boundary(payload: Any) -> None:
    require(isinstance(payload, dict), "chronology result must be an object")
    replay = payload.get("replay")
    materialized = payload.get("materialized")
    require(isinstance(replay, dict), "chronology replay record missing")
    require(isinstance(materialized, dict), "materialization record missing")
    require(
        (
            replay.get("unchanged_discovery_tests_passed"),
            replay.get("unchanged_verifier_tests_passed"),
            replay.get("historical_package_tests_passed"),
        )
        == (14, 36, 50),
        "clean-clone replay test accounting drift",
    )
    omitted = replay.get("verifier_test_08")
    require(isinstance(omitted, dict), "verifier test 08 boundary missing")
    require(
        omitted.get("test_id") == OMITTED_VERIFIER_TEST,
        "verifier test 08 identity drift",
    )
    solver_half = omitted.get("solver_environment_file_half")
    require(
        isinstance(solver_half, dict)
        and solver_half.get("status") == "NOT_REPLAYED_NONBLOCKING",
        "solver-environment boundary was promoted",
    )
    documentary = solver_half.get("documentary_record_audit")
    require(
        isinstance(documentary, dict)
        and documentary.get("documentary_hash_record_count") == 6
        and documentary.get("observed_environment_hash_count") == 0
        and documentary.get("local_environment_files_opened") == 0,
        "documentary solver records were misreported as observed files",
    )
    comparison = replay.get("comparison_execution")
    require(
        isinstance(comparison, dict)
        and comparison.get("unchanged_cli_status") == "NOT_RUN_BY_DESIGN"
        and comparison.get("local_environment_files_opened") == 0,
        "unchanged comparison CLI or local environment was promoted",
    )
    require(
        materialized.get("solver_provenance_files_copied") == 0
        and materialized.get("local_environment_dependency") is False,
        "materialized tree depends on local solver files",
    )


def run_full_replay(*, source_root: Path = REPO) -> dict[str, Any]:
    source_before = {
        "candidate_freeze": sha256_path(
            source_root
            / "verification"
            / "wave33-rooted-construction-candidate-freeze.sha256"
        ),
        "candidate_artifact": sha256_path(
            source_root
            / "attempts"
            / "wave33-rooted-construction"
            / "artifact-manifest.sha256"
        ),
        "verifier_artifact": sha256_path(
            source_root
            / "verification"
            / "wave33-rooted-construction"
            / "artifact-manifest.sha256"
        ),
        "precomparison": sha256_path(
            source_root
            / "verification"
            / "wave33-rooted-construction"
            / "precomparison-freeze.sha256"
        ),
    }
    require(
        source_before
        == {
            "candidate_freeze": CANDIDATE_FREEZE_SHA256,
            "candidate_artifact": CANDIDATE_ARTIFACT_SHA256,
            "verifier_artifact": VERIFIER_ARTIFACT_SHA256,
            "precomparison": PRECOMPARISON_MANIFEST_SHA256,
        },
        "source freeze anchors drifted before replay",
    )

    with tempfile.TemporaryDirectory(prefix="wave33-chronology-") as directory:
        scratch = Path(directory)
        synthetic = scratch / "historical-root"
        outputs = scratch / "outputs"
        outputs.mkdir()
        materialized = materialize_historical_root(
            synthetic, source_root=source_root
        )
        before = tree_snapshot(synthetic)
        environment = isolated_subprocess_environment()
        discovery_dir = (
            synthetic / "attempts" / "wave33-rooted-construction"
        ).resolve()
        verifier_dir = (
            synthetic / "verification" / "wave33-rooted-construction"
        ).resolve()

        discovery_test = run_process(
            [
                sys.executable,
                "-I",
                "-B",
                "-c",
                complete_suite_runner_source(
                    expected_count=14,
                    expected_ids_sha256=DISCOVERY_TEST_IDS_SHA256,
                ),
                str(discovery_dir),
            ],
            cwd=synthetic,
            environment=environment,
        )
        verifier_test = run_process(
            [
                sys.executable,
                "-I",
                "-B",
                "-c",
                filtered_verifier_runner_source(),
                str(verifier_dir),
            ],
            cwd=synthetic,
            environment=environment,
        )
        discovery_count = unittest_count(discovery_test)
        verifier_count = unittest_count(verifier_test)
        discovery_metadata = runner_metadata(discovery_test)
        verifier_metadata = runner_metadata(verifier_test)
        require(discovery_count == 14, "historical discovery test count drift")
        require(verifier_count == 36, "historical verifier test count drift")
        require(
            discovery_metadata
            == {
                "test_count": 14,
                "test_ids_sha256": DISCOVERY_TEST_IDS_SHA256,
            },
            "discovery runner metadata drift",
        )
        require(
            verifier_metadata
            == {
                "full_test_count": 37,
                "full_test_ids_sha256": FULL_VERIFIER_TEST_IDS_SHA256,
                "omitted_test_id": OMITTED_VERIFIER_TEST,
                "selected_test_count": 36,
                "selected_test_ids_sha256":
                    INCLUDED_VERIFIER_TEST_IDS_SHA256,
            },
            "verifier runner metadata drift",
        )

        exact_output = outputs / "exact-results.json"
        run_process(
            [
                sys.executable,
                "-I",
                "-B",
                str(discovery_dir / "exact_check.py"),
                "--partial-certificate",
                str(discovery_dir / "partial-design-certificate.json"),
                "--output",
                str(exact_output),
            ],
            cwd=synthetic,
            environment=environment,
        )
        require(
            sha256_path(exact_output) == EXPECTED_EXACT_RESULTS_SHA256,
            "historical exact replay output hash drift",
        )
        accepted_exact = (
            synthetic
            / "attempts"
            / "wave33-rooted-construction"
            / "exact-results.json"
        )
        require(
            exact_output.read_bytes() == accepted_exact.read_bytes(),
            "historical exact replay is not byte-identical",
        )

        comparison_projection = run_chronology_owned_comparison(synthetic)
        comparison_projection_sha256 = sha256_bytes(
            canonical_json_bytes(comparison_projection)
        )
        exact_import_audit = comparison_projection[
            "exact_checker_import_audit"
        ]
        solver_record_audit = comparison_projection[
            "solver_inspection_records"
        ]

        after = tree_snapshot(synthetic)
        require(before == after, "historical synthetic tree was modified")
        require(
            not any("__pycache__" in path.parts for path in synthetic.rglob("*")),
            "historical replay created __pycache__",
        )

    source_after = {
        "candidate_freeze": sha256_path(
            source_root
            / "verification"
            / "wave33-rooted-construction-candidate-freeze.sha256"
        ),
        "candidate_artifact": sha256_path(
            source_root
            / "attempts"
            / "wave33-rooted-construction"
            / "artifact-manifest.sha256"
        ),
        "verifier_artifact": sha256_path(
            source_root
            / "verification"
            / "wave33-rooted-construction"
            / "artifact-manifest.sha256"
        ),
        "precomparison": sha256_path(
            source_root
            / "verification"
            / "wave33-rooted-construction"
            / "precomparison-freeze.sha256"
        ),
    }
    require(source_before == source_after, "source freeze anchors changed in replay")

    result = {
        "schema_version": 2,
        "role": "verifier",
        "claim_label": "VERIFIED",
        "scope": (
            "Clean-clone-independent historical-byte replay of all 14 "
            "unchanged Wave 33 discovery tests and the 36 unchanged verifier "
            "tests that do not inspect ignored local solver-environment files."
        ),
        "chronology": {
            "live_structure_is_not_historical_input": (
                sha256_path(source_root / "STRUCTURE.md")
                != HISTORICAL_STRUCTURE_SHA256
            ),
            "historical_structure_sha256": HISTORICAL_STRUCTURE_SHA256,
            "historical_input_count": 8,
            "archive_sha256": sha256_path(ARCHIVE),
            "archive_status": "PASS",
        },
        "freeze_anchors": {
            "candidate_freeze_sha256": CANDIDATE_FREEZE_SHA256,
            "candidate_artifact_manifest_sha256": CANDIDATE_ARTIFACT_SHA256,
            "precomparison_manifest_sha256": PRECOMPARISON_MANIFEST_SHA256,
            "verifier_artifact_manifest_sha256": VERIFIER_ARTIFACT_SHA256,
            "status": "UNCHANGED",
        },
        "materialized": materialized,
        "replay": {
            "unchanged_discovery_tests_passed": discovery_count,
            "unchanged_verifier_tests_passed": verifier_count,
            "historical_package_tests_passed": discovery_count + verifier_count,
            "discovery_test_ids_sha256": DISCOVERY_TEST_IDS_SHA256,
            "full_verifier_test_ids_sha256":
                FULL_VERIFIER_TEST_IDS_SHA256,
            "included_verifier_test_ids_sha256":
                INCLUDED_VERIFIER_TEST_IDS_SHA256,
            "verifier_test_08": {
                "test_id": OMITTED_VERIFIER_TEST,
                "composite_test_execution": "NOT_RUN_AS_COMPOSITE",
                "portable_source_audit_half": {
                    "status": "PASS",
                    "canonical_result_sha256":
                        EXPECTED_STATIC_SOURCE_AUDIT_SHA256,
                    "exact_checker_import_audit": exact_import_audit,
                },
                "solver_environment_file_half": {
                    "status": "NOT_REPLAYED_NONBLOCKING",
                    "reason": (
                        "The six ignored local environment files are absent "
                        "from a clean clone, and the recorded solver timeout "
                        "has no evidentiary status."
                    ),
                    "documentary_record_audit": solver_record_audit,
                },
            },
            "exact_results_sha256": EXPECTED_EXACT_RESULTS_SHA256,
            "exact_results_byte_identical": True,
            "comparison_results_sha256": EXPECTED_COMPARISON_RESULTS_SHA256,
            "comparison_execution": {
                "unchanged_cli_status": "NOT_RUN_BY_DESIGN",
                "historical_only_cli_stdout_sha256":
                    EXPECTED_COMPARISON_CLI_STDOUT_SHA256,
                "chronology_owned_projection_sha256":
                    comparison_projection_sha256,
                "hash_pinned_function_calls": True,
                "local_environment_files_opened": 0,
            },
            "comparison_accepted_summary_core_bound": True,
            "hostile_search_certificate_sha256": EXPECTED_CERTIFICATE_SHA256,
            "hostile_search_certificate_byte_identical": True,
            "isolated_python_flags": ["-I", "-B"],
            "python_environment_variables_sanitized": True,
            "synthetic_tree_unchanged": True,
            "checkout_outputs_written": 0,
            "pycache_created": False,
            "status": "PASS",
        },
        "status_wall": {
            "complete_graph_extension": "UNKNOWN",
            "complete_domain_UNSAT_certificate": "NONE",
            "full_rooted_endpoint": "UNKNOWN",
            "n3_708": "UNKNOWN",
            "Conway_99": "UNKNOWN",
            "novelty": "UNKNOWN",
            "timeout_negative_evidence": False,
        },
    }
    assert_status_wall(result)
    assert_clean_clone_boundary(result)
    return result


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    parser.add_argument("--build-archive", action="store_true")
    args = parser.parse_args(list(argv) if argv is not None else None)
    try:
        if args.build_archive:
            require(args.output is not None, "--build-archive requires --output")
            payload = build_archive_payload()
            args.output.write_bytes(canonical_json_bytes(payload))
            print(
                json.dumps(
                    {
                        "archive": str(args.output),
                        "sha256": sha256_path(args.output),
                        "status": "BUILT_AND_HASH_CHECKED",
                    },
                    sort_keys=True,
                )
            )
            return 0
        result = run_full_replay()
        encoded = canonical_json_bytes(result)
        if args.output is None:
            sys.stdout.buffer.write(encoded)
        else:
            args.output.write_bytes(encoded)
            print(
                json.dumps(
                    {
                        "output": str(args.output),
                        "sha256": sha256_path(args.output),
                        "status": "PASS",
                    },
                    sort_keys=True,
                )
            )
        return 0
    except (OSError, ChronologyError) as exc:
        print(json.dumps({"status": "FAIL", "error": str(exc)}, sort_keys=True))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
