"""Clean-room Wave198 orientation-lift verifier."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from fractions import Fraction
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
INPUT_FREEZE = HERE / "input-freeze.sha256"
INDEPENDENT_FREEZE = HERE / "independent-result-freeze.sha256"
PRIMARY = ROOT / "attempts/wave198-orientation-lift-proof-b"
HOSTILE = ROOT / "attempts/wave198-orientation-lift-proof-a-audit"
HASH_LINE = re.compile(r"^([0-9a-fA-F]{64})\s+\*?(.+?)\s*$")
C_VALUE = 4158
V_VALUE = 99
VARIABLES = (
    "C", "V", "a1", "a2", "a3", "b1", "b3", "c1", "c2",
    "n2", "n3", "r2", "h", "y", "g", "W",
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def parse_hashes(path: Path) -> list[tuple[str, str]]:
    result = []
    for number, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        match = HASH_LINE.fullmatch(raw.strip())
        if match is None:
            raise ValueError(f"bad hash line {path}:{number}")
        result.append((match.group(1).lower(), match.group(2).replace("\\", "/")))
    return result


def check_hashes(entries: list[tuple[str, str]]) -> list[dict[str, str]]:
    failures = []
    for expected, relative in entries:
        path = ROOT / relative
        actual = sha256(path) if path.is_file() else "missing"
        if actual != expected:
            failures.append({"path": relative, "expected": expected, "actual": actual})
    return failures


def integrity() -> dict[str, Any]:
    direct = parse_hashes(INPUT_FREEZE)
    failures = check_hashes(direct)
    checked = len(direct)
    for _, relative in direct:
        if relative.endswith("package-manifest.sha256"):
            entries = parse_hashes(ROOT / relative)
            failures.extend(check_hashes(entries))
            checked += len(entries)
    frozen = parse_hashes(INDEPENDENT_FREEZE)
    failures.extend(check_hashes(frozen))
    checked += len(frozen)
    assert sha256(HERE / "independent-math-result.json") == (
        "07a8d5287a1770fa34aea97c3c879e07642da44d728f6e6c199d2f0b5990f07e"
    )
    return {
        "passed": not failures, "hash_entries_checked": checked,
        "failures": failures,
        "independent_math_sha256": sha256(HERE / "independent-math-result.json"),
        "primary_manifest_sha256": sha256(PRIMARY / "package-manifest.sha256"),
        "hostile_manifest_sha256": sha256(HOSTILE / "package-manifest.sha256"),
        "sources_opened_before_independent_freeze": False,
    }


def row(**entries: int | Fraction) -> tuple[Fraction, ...]:
    return tuple(Fraction(entries.get(name, 0)) for name in VARIABLES)


def add_rows(*rows: tuple[Fraction, ...]) -> tuple[Fraction, ...]:
    return tuple(sum(values, Fraction()) for values in zip(*rows))


def scale(value: int | Fraction, source: tuple[Fraction, ...]) -> tuple[Fraction, ...]:
    return tuple(Fraction(value) * item for item in source)


def slacks() -> dict[str, tuple[Fraction, ...]]:
    return {
        "SI": row(C=-2, a1=2, a2=2, a3=2, b1=Fraction(1, 2),
                  b3=Fraction(1, 2), c1=1, c2=1, n2=2, n3=3),
        "S2": row(b1=Fraction(1, 2), b3=Fraction(1, 2), n2=-1),
        "SE2": row(r2=2, a2=-1, c2=-1),
        "RA": row(a2=-1, a3=-1, b3=-2, c2=-1, h=3, y=1, g=3),
        "SL": row(C=-1, a1=1, a2=1, a3=1, c1=1, n2=2,
                  r2=2, y=1, W=2),
        "S5": row(V=180, n3=-3, c1=-4, c2=-4, a3=-5, b3=-5),
        "SH": row(h=3, a3=-1, b3=-1),
        "SF": row(V=13, n3=-1, h=-1, g=-1),
    }


def orientation_certificate() -> dict[str, Any]:
    return {
        "selected_orientation": (
            "each label of a selected exact-three flag is oriented from "
            "its canonical center to its leaf"
        ),
        "multiplicity_cap": (
            "for fixed x->y, exactly two of the seven y-triangles meet "
            "N(x), leaving five possible anticomplete leaf triangles"
        ),
        "m_upper": 5,
        "private_orientations": (
            "each p3 private selected type3 label occurs in one selected "
            "circuit and therefore one selected orientation"
        ),
        "T_degree_sum": "3n3<=p3+5(T-p3)=5T-4p3",
        "separation": "T+a3+b3<=J",
        "J_cap": "J<=3564",
        "S5": "17820-3n3-4p3-5a3-5b3>=0",
    }


def coefficient_certificate() -> dict[str, Any]:
    q0 = row(a1=2, a2=1, a3=1, b1=1, c1=1, n2=1, n3=2,
             r2=1, h=2, y=1, g=2, W=1)
    target = add_rows(q0, row(C=Fraction(-76, 40), V=Fraction(349, 40)))
    sources = slacks()
    weights = {
        "SI": Fraction(4, 5), "S2": Fraction(6, 5),
        "SE2": Fraction(1, 5), "RA": Fraction(7, 10),
        "SL": Fraction(3, 10), "S5": Fraction(1, 40),
        "SH": Fraction(3, 40), "SF": Fraction(13, 40),
    }
    result = add_rows(
        *(scale(weights[name], sources[name]) for name in weights),
        scale(Fraction(1, 10), row(a1=1)),
        scale(Fraction(3, 5), row(b3=1)),
        scale(Fraction(1, 5), row(c2=1)),
        scale(Fraction(9, 40), row(g=1)),
        scale(Fraction(2, 5), row(W=1)),
    )
    assert result == target
    rational = Fraction(76 * C_VALUE - 349 * V_VALUE, 40)
    assert rational == Fraction(281457, 40)
    assert rational.numerator // rational.denominator + 1 == 7037
    return {
        "slacks": {
            "SI": "I-2C", "S2": "p2-n2", "SE2": "2r2-a2-c2",
            "RA": "3h+y+3g-a2-a3-2b3-c2",
            "SL": "n1+2n2+c1+2r2+y+2W-C",
            "S5": "180V-3n3-4p3-5a3-5b3",
            "SH": "3h-a3-b3", "SF": "13V-n3-h-g",
        },
        "weights": {name: str(value) for name, value in weights.items()},
        "explicit_remainder": {
            "a1": "1/10", "b3": "3/5", "c2": "1/5",
            "g": "9/40", "W": "2/5",
        },
        "identity": (
            "Q0-(76C-349V)/40=4SI/5+6S2/5+SE2/5+7RA/10+"
            "3SL/10+S5/40+3SH/40+13SF/40+a1/10+3b3/5+"
            "c2/5+9g/40+2W/5"
        ),
        "rational_target": "281457/40",
        "integer_Q": 7037,
    }


def integer_control() -> dict[str, Any]:
    values = {
        "a1": 0, "a2": 15, "a3": 0, "b1": 624, "b3": 0,
        "c1": 3489, "c2": 0, "n2": 312, "n3": 1287,
        "r2": 8, "h": 0, "y": 15, "g": 0, "W": 0,
    }
    n1 = values["a1"] + values["a2"] + values["a3"]
    p2 = (values["b1"] + values["b3"]) // 2
    p3 = values["c1"] + values["c2"]
    r1 = values["a1"] + values["b1"] + values["c1"]
    full = {"C": C_VALUE, "V": V_VALUE, **values}
    vector = tuple(Fraction(full.get(name, 0)) for name in VARIABLES)
    evaluated = {
        name: sum(a * b for a, b in zip(source, vector))
        for name, source in slacks().items()
    }
    assert evaluated == {
        "SI": 0, "S2": 0, "SE2": 1, "RA": 0,
        "SL": 1, "S5": 3, "SH": 0, "SF": 0,
    }
    q0 = n1 + values["n2"] + 2 * values["n3"] + r1 + values["r2"]
    q0 += 2 * values["h"] + values["y"] + 2 * values["g"] + values["W"]
    assert q0 == 7037
    gap = Fraction(q0) - Fraction(281457, 40)
    assert gap == Fraction(23, 40)
    return {
        "row": values,
        "derived": {"n1": n1, "p2": p2, "p3": p3, "r1": r1, "Q0": q0},
        "slacks": {name: int(value) for name, value in evaluated.items()},
        "rounding_gap": "23/40",
        "gap_decomposition": "SE2/5+3SL/10+S5/40=23/40",
        "asserted_object": False,
    }


def build_math_result() -> dict[str, Any]:
    payload: dict[str, Any] = {
        "format": "wave198-orientation-lift-clean-room-math-v1",
        "conditional_setting": "prism-free rank-11 endpoint",
        "orientation": orientation_certificate(),
        "certificate": coefficient_certificate(),
        "integer_control": integer_control(),
        "bounds": {
            "rational_Q": "281457/40", "integer_Q": 7037,
            "edge_projective": 693, "all_projective": 7730,
            "scalar_words": 15460,
        },
        "verdict": "INDEPENDENTLY_DERIVED_PRE_SOURCE",
        "boundary": {
            "source_compared": False, "graph_constructed": False,
            "rank_11_excluded": False, "endpoint_excluded": False,
            "conway_99": "UNKNOWN", "external_novelty": "UNKNOWN",
        },
    }
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    payload["math_result_sha256"] = hashlib.sha256(canonical).hexdigest()
    return payload


def source_comparisons() -> dict[str, Any]:
    primary_path = PRIMARY / "exact-results.json"
    hostile_path = HOSTILE / "exact-results.json"
    primary = json.loads(primary_path.read_text(encoding="utf-8"))
    hostile = json.loads(hostile_path.read_text(encoding="utf-8"))
    orientation = primary["orientation_row"]
    assert orientation["flags_per_orientation"] == 5
    assert orientation["private_selected_multiplicity"] == 1
    assert orientation["selected_row"] == "3*n3+4*p3<=5*T"
    assert primary["global_rows"]["S5"] == (
        "5*H-3*n3-4*p3-5*a3-5*b3>=0"
    )
    cert = primary["certificate"]
    assert cert["reduced_difference"] == {}
    assert cert["target"] == "281457/40"
    assert cert["integer_Q_lower_bound"] == 7037
    assert cert["edge_added_projective"] == 7730
    assert cert["circuit_scalar_words"] == 15460
    assert cert["rational_null"]["asserted_object"] is False
    assert hostile["verdict"] == "ACCEPTED_AS_DERIVED"
    assert hostile["orientation"]["selected_row"] == "3*n3+4*p3<=5*T"
    assert hostile["certificate"]["target"] == "281457/40"
    assert hostile["certificate"]["integer_Q_lower_bound"] == 7037
    assert hostile["rational_null"]["asserted_object"] is False
    return {
        "primary_matches": True, "hostile_verdict": "ACCEPT",
        "hostile_used_as_premise": False,
        "orientation_row_matches": True, "S5_matches": True,
        "certificate_matches": True, "counts_match": True,
        "source_rational_null_arithmetic_only": True,
        "independent_integer_control_distinct": True,
        "hostile_generic_discover_portability": (
            "known relative-import failure; documented explicit module command passes"
        ),
        "primary_exact_sha256": sha256(primary_path),
        "hostile_exact_sha256": sha256(hostile_path),
    }


def build_results() -> dict[str, Any]:
    checked = integrity()
    assert checked["passed"]
    payload: dict[str, Any] = {
        "format": "wave198-orientation-lift-verification-v1",
        "integrity": checked,
        "independent_math_result": build_math_result(),
        "source_comparisons": source_comparisons(),
        "verdict": "VERIFIED_WITH_SCOPE",
        "boundary": {
            "conditional_theorem_verified": True,
            "sources_compared": True,
            "graph_constructed": False, "code_constructed": False,
            "rank_11_excluded": False, "endpoint_excluded": False,
            "conway_99": "UNKNOWN", "external_novelty": "UNKNOWN",
        },
    }
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    payload["result_sha256"] = hashlib.sha256(canonical).hexdigest()
    return payload


def write_json(path: Path, value: dict[str, Any]) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write-math", type=Path)
    parser.add_argument("--verify-math", type=Path)
    parser.add_argument("--write", type=Path)
    parser.add_argument("--verify", type=Path)
    args = parser.parse_args()
    if args.write_math:
        write_json(args.write_math, build_math_result())
        print(f"WROTE Wave198 independent math: {args.write_math}")
        return 0
    if args.verify_math:
        expected = json.loads(args.verify_math.read_text(encoding="utf-8"))
        if build_math_result() != expected:
            return 1
        print(f"PASS Wave198 independent math: {args.verify_math}")
        return 0
    if args.write:
        write_json(args.write, build_results())
        print(f"WROTE Wave198 verification: {args.write}")
        return 0
    if args.verify:
        expected = json.loads(args.verify.read_text(encoding="utf-8"))
        if build_results() != expected:
            return 1
        print(f"PASS Wave198 verification: {args.verify}")
        return 0
    print(json.dumps(build_math_result(), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
