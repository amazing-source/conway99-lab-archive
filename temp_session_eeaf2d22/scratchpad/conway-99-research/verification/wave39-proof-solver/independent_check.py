#!/usr/bin/env python3
"""Independent byte-level and semantic check of the Wave 39 proof shard."""

from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import re
import shlex
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
ATTEMPT = ROOT / "attempts" / "wave39-proof-solver"
SOURCE = ROOT / "attempts" / "wave37-proof-producing-endpoint" / "branch-15.opb.gz"
SOURCE_GZIP_SHA = "7683599142bfb51dc2d461d56fc1820bc58c658ed5167b17b5004473b589933e"
SOURCE_RAW_SHA = "4c1607f4aef7e20569592ccb4ac20dfe30c1e1d220a8fbc0a202554bed6d84e5"
SHARD_RAW_SHA = "8ed7ae5b893191ed2c342c681084a8f9f67cab6f1b6728aa8c8f0793e04e1c11"
SHARD_GZIP_SHA = "6a5e88245acb4dece760ce67e39fa9b098e43c958bc0f164bcba9f67e8ea4e2d"
RAW_PROOF_SHA = "b2fcb06206d8a09ab636535f0358f6013e5daddaf14b7132180698a2f59340d5"
KERNEL_PROOF_SHA = "5645dded139847ff144e84ddc6dd59e90267a9c585a986f13e20748b773c07a0"
TERM = re.compile(r"\+1\s+(~)?x([1-9][0-9]*)")
CONSTRAINT = re.compile(
    r"^(?:\+1\s+(?:~)?x[1-9][0-9]*\s+)+>=\s+([0-9]+)\s+;\s*$"
)


def sha(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def parse(text: str) -> tuple[list[tuple[int, bool]], int]:
    match = CONSTRAINT.fullmatch(text)
    if match is None:
        raise ValueError("unsupported constraint syntax")
    literals = [
        (int(term.group(2)), term.group(1) is None)
        for term in TERM.finditer(text)
    ]
    if len({variable for variable, _ in literals}) != len(literals):
        raise ValueError("duplicate variable in constraint")
    return literals, int(match.group(1))


def load_source() -> tuple[bytes, dict[int, str]]:
    compressed = SOURCE.read_bytes()
    if sha(compressed) != SOURCE_GZIP_SHA:
        raise ValueError("source gzip digest mismatch")
    raw = gzip.decompress(compressed)
    if sha(raw) != SOURCE_RAW_SHA:
        raise ValueError("source raw digest mismatch")
    lines = raw.splitlines()
    if lines[0] != b"* #variable= 289338 #constraint= 574615":
        raise ValueError("source header mismatch")
    if len(lines) != 574616:
        raise ValueError("source constraint count mismatch")
    selected = {
        number: lines[number - 1].decode("ascii")
        for number in (106, 285938, 286004, 571132)
    }
    return raw, selected


def check_local_argument(selected: dict[int, str]) -> None:
    expected = {
        106: [(24, False), (187, False), (3591, True)],
        285938: [(24, True)],
        286004: [(2, True)],
    }
    for number, literals in expected.items():
        parsed, bound = parse(selected[number])
        if parsed != literals or bound != 1:
            raise ValueError(f"unexpected source line {number}")
    capacity, bound = parse(selected[571132])
    expected_capacity = [(variable, False) for variable in range(3569, 3651)]
    expected_capacity.append((2, False))
    if capacity != expected_capacity or bound != 82:
        raise ValueError("unexpected capacity constraint")

    assignments = {24: True, 2: True, 187: True}
    satisfied = sum(
        assignments[variable] == polarity
        for variable, polarity in capacity
        if variable in assignments
    )
    unknown = [
        (variable, polarity)
        for variable, polarity in capacity
        if variable not in assignments
    ]
    if (satisfied, len(unknown), satisfied + len(unknown), bound) != (0, 82, 82, 82):
        raise ValueError("capacity is not tight under x2=1")
    # Tightness forces every unknown literal, in particular ~x3591.
    assignments[3591] = False
    wedge, wedge_bound = parse(selected[106])
    maximum = sum(
        assignments[variable] == polarity
        for variable, polarity in wedge
        if variable in assignments
    ) + sum(variable not in assignments for variable, _ in wedge)
    if maximum >= wedge_bound:
        raise ValueError("wedge does not contradict the assignments")


def check_shard_transform(source_raw: bytes) -> None:
    raw_path = ATTEMPT / "branch-15-x187-positive.opb"
    gzip_path = ATTEMPT / "branch-15-x187-positive.opb.gz"
    raw = raw_path.read_bytes()
    compressed = gzip_path.read_bytes()
    if (len(raw), sha(raw)) != (29827719, SHARD_RAW_SHA):
        raise ValueError("raw shard mismatch")
    if (len(compressed), sha(compressed)) != (3854316, SHARD_GZIP_SHA):
        raise ValueError("compressed shard mismatch")
    if gzip.decompress(compressed) != raw:
        raise ValueError("compressed and raw shards differ")
    source_header, source_body = source_raw.split(b"\n", 1)
    expected = (
        b"* #variable= 289338 #constraint= 574616\n"
        + source_body
        + b"+1 x187 >= 1 ;\n"
    )
    if source_header != b"* #variable= 289338 #constraint= 574615":
        raise ValueError("unexpected source header")
    if raw != expected:
        raise ValueError("shard is not the exact append-unit transform")


def check_metadata() -> None:
    certificate = json.loads(
        (ATTEMPT / "branch-15-x187-positive-certificate.json").read_text("utf-8")
    )
    if certificate["claim_label"] != "CANDIDATE":
        raise ValueError("discovery certificate status inflated")
    if certificate["coverage"] != {
        "closed_endpoint_cases": 0,
        "closed_shard": "branch15 AND x187=1",
        "closed_shards": 1,
        "exhaustive_polarity_shards": 2,
        "open_shard": "branch15 AND x187=0",
        "total_endpoint_cases": 33,
    }:
        raise ValueError("coverage boundary mismatch")
    formula = json.loads(
        (ATTEMPT / "branch-15-x187-positive-formula.json").read_text("utf-8")
    )
    if formula["opb"]["raw_sha256"] != SHARD_RAW_SHA:
        raise ValueError("formula raw digest mismatch")
    if formula["opb"]["gzip_sha256"] != SHARD_GZIP_SHA:
        raise ValueError("formula gzip digest mismatch")


def check_proof_artifacts() -> None:
    raw_proof = (ATTEMPT / "branch-15-x187-positive.raw.pbp").read_bytes()
    kernel_proof = (ATTEMPT / "branch-15-x187-positive.kernel.pbp").read_bytes()
    if sha(raw_proof) != RAW_PROOF_SHA or sha(kernel_proof) != KERNEL_PROOF_SHA:
        raise ValueError("proof digest mismatch")
    for name in (
        "branch-15-x187-positive.raw-check.txt",
        "branch-15-x187-positive.elaborate.txt",
        "branch-15-x187-positive.kernel-check.txt",
    ):
        if (ATTEMPT / name).read_text("ascii") != (
            "Running VeriPB version 3.0.2\ns VERIFIED UNSATISFIABLE\n"
        ):
            raise ValueError(f"unexpected checker transcript: {name}")
    if (ATTEMPT / "branch-15-x187-positive.cakepb.txt").exists():
        raise ValueError("an unsupported CakePB conclusion artifact is present")


def wsl_path(path: Path) -> str:
    drive = path.drive.rstrip(":").lower()
    return f"/mnt/{drive}/" + "/".join(path.resolve().parts[1:])


def replay_veripb() -> dict[str, str]:
    repo = shlex.quote(wsl_path(ROOT))
    veripb = "/home/researcher/.cache/conway-tools/veripb-install/bin/veripb"
    opb = "attempts/wave39-proof-solver/branch-15-x187-positive.opb"
    results = {}
    for label, proof in (
        ("raw", "attempts/wave39-proof-solver/branch-15-x187-positive.raw.pbp"),
        ("kernel", "attempts/wave39-proof-solver/branch-15-x187-positive.kernel.pbp"),
    ):
        command = (
            f"cd {repo} && {veripb} --force-checked-deletion "
            f"{shlex.quote(opb)} {shlex.quote(proof)}"
        )
        completed = subprocess.run(
            ["wsl.exe", "-e", "bash", "--noprofile", "--norc", "-lc", command],
            check=False,
            capture_output=True,
            text=True,
            timeout=120,
        )
        output = completed.stdout + completed.stderr
        if completed.returncode != 0 or "s VERIFIED UNSATISFIABLE" not in output:
            raise ValueError(f"independent VeriPB {label} replay failed")
        results[label] = "VERIFIED_UNSATISFIABLE"
    return results


def verify(run_veripb: bool = False) -> dict[str, object]:
    source_raw, selected = load_source()
    check_local_argument(selected)
    check_shard_transform(source_raw)
    check_metadata()
    check_proof_artifacts()
    result: dict[str, object] = {
        "claim_label": "VERIFIED",
        "scope": "branch15 AND x187=1 only",
        "generalized_unit_argument": "PASS",
        "entailed_literal_in_branch_15": "x187=0",
        "closed_shards": 1,
        "closed_endpoint_cases": 0,
        "total_endpoint_cases": 33,
        "branch_15_status": "UNKNOWN",
        "endpoint_status": "UNKNOWN",
        "upper_bound_improved_below_4158": False,
        "proof_artifact_hashes": "PASS",
        "cakepb": "NO_CONCLUSION_NOT_REPLAYED",
    }
    result["independent_veripb"] = (
        replay_veripb() if run_veripb else "NOT_RUN_BY_THIS_INVOCATION"
    )
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--run-veripb", action="store_true")
    args = parser.parse_args()
    result = verify(args.run_veripb)
    args.output.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
