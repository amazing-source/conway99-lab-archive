#!/usr/bin/env python3
"""Record and fail-closed check the bounded branch-15 remainder experiment."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
ATTEMPT_ROOT = Path(__file__).resolve().parent
FORMULA_METADATA = ATTEMPT_ROOT / "branch-15-x187-zero-formula.json"
FORMULA_GZIP = ATTEMPT_ROOT / "branch-15-x187-zero.opb.gz"
FORMULA_RAW = ATTEMPT_ROOT / "branch-15-x187-zero.opb"
RAW_PROOF = ATTEMPT_ROOT / "branch-15-x187-zero.raw.pbp"
KERNEL_PROOF = ATTEMPT_ROOT / "branch-15-x187-zero.kernel.pbp"
SOLVER_TRANSCRIPT = ATTEMPT_ROOT / "branch-15-x187-zero.solver.txt"
VERIPB_RAW = ATTEMPT_ROOT / "branch-15-x187-zero.veripb-raw.txt"
VERIPB_ELABORATE = ATTEMPT_ROOT / "branch-15-x187-zero.veripb-elaborate.txt"
VERIPB_KERNEL = ATTEMPT_ROOT / "branch-15-x187-zero.veripb-kernel.txt"
CAKEPB_TRANSCRIPT = ATTEMPT_ROOT / "branch-15-x187-zero.cakepb.txt"

TOOL_HASHES = {
    "Exact": "842ac70b4e938d24f537a56513ff64ea845206c714ce34da467ce146c5c5c928",
    "VeriPB": "635b6f2fbd7a7fb98bf7a1f7af038355a1e58438cfdc1ee4e2649979017ace36",
    "CakePB": "5920919642b1c498c2654a849fcd894ea18e7736ebf32919a9a8915861033e46",
}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def read_process_text(path: Path) -> str:
    raw = path.read_bytes()
    if raw.startswith(b"\xff\xfe"):
        text = raw.decode("utf-16")
    else:
        text = raw.decode("utf-8")
    return text.replace("\r\n", "\n")


def metric(transcript: str, name: str) -> int | float:
    match = re.search(rf"^c {re.escape(name)} ([0-9]+(?:\.[0-9]+)?)$", transcript, re.M)
    if match is None:
        raise ValueError(f"missing Exact metric {name!r}")
    raw = match.group(1)
    return float(raw) if "." in raw else int(raw)


def relative(path: Path) -> str:
    return path.relative_to(REPOSITORY_ROOT).as_posix()


def build() -> dict[str, object]:
    metadata = json.loads(FORMULA_METADATA.read_text(encoding="utf-8"))
    if metadata["format"] != "wave53-branch15-x187-zero-opb-v1":
        raise ValueError("wrong formula metadata format")
    if metadata["status"] != "CANDIDATE_FORMULA_ONLY":
        raise ValueError("formula status inflated")
    if metadata["opb"]["raw_sha256"] != sha256_file(FORMULA_RAW):
        raise ValueError("raw formula hash mismatch")
    if metadata["opb"]["gzip_sha256"] != sha256_file(FORMULA_GZIP):
        raise ValueError("compressed formula hash mismatch")

    solver = read_process_text(SOLVER_TRANSCRIPT)
    if "\ns UNKNOWN\n" not in f"\n{solver}":
        raise ValueError("Exact transcript is not UNKNOWN")
    if "s SATISFIABLE" in solver or "s UNSATISFIABLE" in solver:
        raise ValueError("Exact transcript contains a terminal result")
    for transcript in (VERIPB_RAW, VERIPB_ELABORATE, VERIPB_KERNEL):
        text = read_process_text(transcript)
        if "s VERIFIED NO CONCLUSION" not in text:
            raise ValueError(f"VeriPB did not verify NO CONCLUSION: {transcript.name}")
    cake = read_process_text(CAKEPB_TRANSCRIPT)
    if "s VERIFIED NO CONCLUSION" not in cake:
        raise ValueError("CakePB did not verify NO CONCLUSION")

    artifacts = [
        FORMULA_METADATA,
        FORMULA_GZIP,
        RAW_PROOF,
        KERNEL_PROOF,
        SOLVER_TRANSCRIPT,
        VERIPB_RAW,
        VERIPB_ELABORATE,
        VERIPB_KERNEL,
        CAKEPB_TRANSCRIPT,
    ]
    return {
        "format": "wave53-bounded-proof-run-v1",
        "role": "proof_a",
        "claim_label": "CANDIDATE",
        "scope": "three-second Exact run on branch15 AND x187=0 with retained proof replay",
        "tool_hashes": TOOL_HASHES,
        "formula": {
            "metadata_path": relative(FORMULA_METADATA),
            "metadata_sha256": sha256_file(FORMULA_METADATA),
            "gzip_path": relative(FORMULA_GZIP),
            "gzip_sha256": sha256_file(FORMULA_GZIP),
            "raw_sha256": sha256_file(FORMULA_RAW),
            "constraints_declared": metadata["opb"]["constraints"],
        },
        "commands": [
            (
                "Exact --timeout=3 --proof-assumptions=0 "
                "--proof-log=branch-15-x187-zero.raw.pbp "
                "branch-15-x187-zero.opb"
            ),
            (
                "veripb --force-checked-deletion branch-15-x187-zero.opb "
                "branch-15-x187-zero.raw.pbp"
            ),
            (
                "veripb --force-checked-deletion --elaborate "
                "branch-15-x187-zero.kernel.pbp branch-15-x187-zero.opb "
                "branch-15-x187-zero.raw.pbp"
            ),
            (
                "veripb --force-checked-deletion branch-15-x187-zero.opb "
                "branch-15-x187-zero.kernel.pbp"
            ),
            "cake_pb branch-15-x187-zero.opb branch-15-x187-zero.kernel.pbp",
        ],
        "artifacts": {
            relative(path): {
                "bytes": path.stat().st_size,
                "sha256": sha256_file(path),
            }
            for path in artifacts
        },
        "exact": {
            "result": "UNKNOWN",
            "solver_timeout_setting_seconds": 3,
            "timeout_is_strict_process_wall": False,
            "cpu_seconds": metric(solver, "cpu time"),
            "parse_seconds": metric(solver, "parse time"),
            "solve_seconds": metric(solver, "solve time"),
            "propagations": metric(solver, "propagations"),
            "decisions": metric(solver, "decisions"),
            "conflicts": metric(solver, "conflicts"),
            "solutions": metric(solver, "solutions"),
            "unit_literals_derived": metric(solver, "unit literals derived"),
        },
        "proof_replay": {
            "raw_veripb": "VERIFIED_NO_CONCLUSION",
            "elaboration_veripb": "VERIFIED_NO_CONCLUSION",
            "kernel_veripb": "VERIFIED_NO_CONCLUSION",
            "kernel_cakepb": "VERIFIED_NO_CONCLUSION",
        },
        "resource_guard": {
            "required_free_memory_percent": 20,
            "historical_discovery_reported_free_memory_percent_before": 57.46,
            "historical_discovery_reported_free_memory_percent_after": 56.25,
            "raw_monitor_transcript_retained": False,
            "historical_guard_status": "SELF_REPORTED_NOT_INDEPENDENTLY_REPLAYABLE",
        },
        "conclusion": {
            "mathematical_evidence": "NONE",
            "complete_endpoint_cases_closed": 0,
            "complete_endpoint_cases_total": 33,
            "proof_coverage": "0/33",
            "branch15_status": "UNKNOWN",
            "endpoint_status": "UNKNOWN",
        },
        "limitations": [
            "The checked proof certifies only that the bounded run made no conclusion.",
            "Only 0.103 seconds were spent solving after parsing and presolve.",
            "A retained partial proof is not an UNSAT certificate.",
            "Historical discovery RAM percentages have no raw monitor transcript and are not mathematical evidence.",
            "No complete case, endpoint, upper bound, graph, or novelty claim follows.",
        ],
    }


def canonical_json(value: object) -> str:
    return json.dumps(value, indent=2, sort_keys=True) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output", type=Path, default=ATTEMPT_ROOT / "bounded-run.json"
    )
    arguments = parser.parse_args()
    arguments.output.write_text(
        canonical_json(build()), encoding="utf-8", newline="\n"
    )
    print(f"wrote {arguments.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
