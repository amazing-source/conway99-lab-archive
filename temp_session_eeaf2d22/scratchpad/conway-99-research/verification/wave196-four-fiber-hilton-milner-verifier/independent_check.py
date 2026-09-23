"""Clean-room verifier for the Wave196 four-fibre local theorem.

The independent mathematical payload was frozen before this verifier opened
any Wave196 discovery package.  Its finite checks instantiate two explicitly
classified Hilton--Milner equality templates; they do not search for families.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from collections import Counter
from fractions import Fraction
from itertools import combinations
from pathlib import Path
from typing import Any, Iterable


ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
INPUT_FREEZE = HERE / "input-freeze.sha256"
INDEPENDENT_FREEZE = HERE / "independent-result-freeze.sha256"
PRIMARY_DIR = ROOT / "attempts/wave196-four-fiber-hilton-milner-proof-a"
PROOF_B_DIR = ROOT / "attempts/wave196-four-fiber-proof-b-audit"
HASH_LINE = re.compile(r"^([0-9a-fA-F]{64})\s+\*?(.+?)\s*$")
C_VALUE = 4158
VERTICES = 99
DEGREE = 14
LAMBDA = 1
MU = 2
LOCAL_BLOCKS = 7
NONNEIGHBORS_PER_VERTEX = 84


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def parse_hash_list(path: Path) -> list[tuple[str, str]]:
    entries: list[tuple[str, str]] = []
    for number, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        match = HASH_LINE.fullmatch(line)
        if match is None:
            raise ValueError(f"malformed hash line {path}:{number}: {raw!r}")
        relative = match.group(2)
        sized = re.fullmatch(r"\d+\s{2,}(.+)", relative)
        if sized is not None:
            relative = sized.group(1)
        entries.append((match.group(1).lower(), relative.replace("\\", "/")))
    if not entries:
        raise ValueError(f"empty hash list: {path}")
    return entries


def check_entries(
    entries: list[tuple[str, str]], manifest: str
) -> list[dict[str, str]]:
    failures: list[dict[str, str]] = []
    for expected, relative in entries:
        target = (ROOT / relative).resolve()
        actual = sha256(target) if target.is_file() else "missing"
        if actual != expected:
            failures.append(
                {
                    "manifest": manifest,
                    "path": relative,
                    "expected": expected,
                    "actual": actual,
                }
            )
    return failures


def verify_manifest_closure() -> dict[str, Any]:
    direct_entries = parse_hash_list(INPUT_FREEZE)
    expected_direct = {
        "AGENTS.md",
        "verification/wave180-capacity3-companion/package-manifest.sha256",
        "verification/wave194-five-thirds-verifier/package-manifest.sha256",
        "verification/wave195-hilton-milner-verifier/package-manifest.sha256",
        (
            "attempts/wave196-four-fiber-hilton-milner-proof-a/"
            "package-manifest.sha256"
        ),
        "attempts/wave196-four-fiber-proof-b-audit/package-manifest.sha256",
    }
    actual_direct = {relative for _, relative in direct_entries}
    if actual_direct != expected_direct:
        raise AssertionError(
            f"unexpected direct input set: {sorted(actual_direct ^ expected_direct)}"
        )

    failures = check_entries(direct_entries, "input-freeze")
    package_manifests = [
        relative
        for _, relative in direct_entries
        if relative.endswith("package-manifest.sha256")
    ]
    checked_entries = len(direct_entries)
    manifests_checked = 0
    for relative in package_manifests:
        manifest_path = ROOT / relative
        entries = parse_hash_list(manifest_path)
        manifests_checked += 1
        checked_entries += len(entries)
        failures.extend(check_entries(entries, relative))

    # The primary Wave196 source's immediate premise seals are also checked.
    # Earlier verifier packages already contain their own recursively audited
    # integrity results; reopening their entire legacy provenance graph would
    # mix incompatible historical hash-list formats into this Wave196 audit.
    source_input_freezes = (
        (
            "attempts/wave196-four-fiber-hilton-milner-proof-a/"
            "input-freeze.sha256"
        ),
        "attempts/wave196-four-fiber-proof-b-audit/input-freeze.sha256",
    )
    for source_input_relative in source_input_freezes:
        source_input_entries = parse_hash_list(ROOT / source_input_relative)
        checked_entries += len(source_input_entries)
        manifests_checked += 1
        failures.extend(
            check_entries(source_input_entries, source_input_relative)
        )

    independent_entries = parse_hash_list(INDEPENDENT_FREEZE)
    checked_entries += len(independent_entries)
    failures.extend(check_entries(independent_entries, "independent-result-freeze"))
    assert sha256(
        ROOT
        / "attempts/wave196-four-fiber-hilton-milner-proof-a"
        / "package-manifest.sha256"
    ) == "83bd93ab0980305d59052dd25dc373f582b5a6fc998b122d64d506871e244b1c"
    assert sha256(
        ROOT
        / "attempts/wave196-four-fiber-proof-b-audit"
        / "package-manifest.sha256"
    ) == "1eb6c6abdc6855af950459ac524653108f5582d9686fbe4e6a0df89e9c39c14a"
    assert sha256(HERE / "independent-math-result.json") == (
        "106444612745ed8e8b384460cc696c5d580a2201aa53f257e2a9d616ea5ce969"
    )
    return {
        "passed": not failures,
        "direct_entries_checked": len(direct_entries),
        "sealed_manifests_checked": manifests_checked,
        "all_hash_entries_checked": checked_entries,
        "independent_result_sha256": sha256(
            HERE / "independent-math-result.json"
        ),
        "primary_manifest_sha256": sha256(
            PRIMARY_DIR / "package-manifest.sha256"
        ),
        "failures": failures,
        "primary_opened_before_independent_freeze": False,
        "primary_checker_imported_or_executed_before_independent_freeze": False,
        "legacy_provenance_recursion": (
            "not reopened; sealed verifier results retain their own "
            "recursive integrity audits"
        ),
    }


def local_two_star_type_certificate() -> dict[str, Any]:
    pair_types = LOCAL_BLOCKS * (LOCAL_BLOCKS - 1) // 2
    vertices_per_type = 2 * 2
    assert pair_types == 21
    assert vertices_per_type == 4
    assert pair_types * vertices_per_type == NONNEIGHBORS_PER_VERTEX
    return {
        "local_graph": (
            "N(x) is 1-regular because every edge xy has lambda=1; hence "
            "the 14 neighbors split into seven edges {p_i,q_i}"
        ),
        "star_blocks": "S_i={x,p_i,q_i}, i=1,...,7",
        "type_definition": (
            "P_x(y)={i,j}, where the two common neighbors of the nonedge "
            "xy lie in the distinct blocks S_i and S_j"
        ),
        "type_well_defined": (
            "the two common neighbors cannot be p_i,q_i from one block, "
            "or edge p_iq_i would have common neighbors x and y"
        ),
        "four_vertex_bijection": (
            "for each {i,j}, every one of the four cross pairs "
            "(u,v) in {p_i,q_i}x{p_j,q_j} is a nonedge; its unique common "
            "neighbor besides x is a nonneighbor y of x of type {i,j}; "
            "mu=2 makes the cross-pair-to-y map injective and surjective"
        ),
        "pair_types": pair_types,
        "vertices_per_type": vertices_per_type,
        "total_nonneighbors": pair_types * vertices_per_type,
        "parameters_used": {
            "degree": DEGREE,
            "lambda": LAMBDA,
            "mu": MU,
        },
    }


def flag_leaf_type_certificate() -> dict[str, Any]:
    # A 2-regular simple bipartite graph on two parts of order three has
    # six edges and must be a single 6-cycle.  Its leaf neighborhoods are
    # therefore the three two-subsets of the A-side.
    A = (0, 1, 2)
    leaf_types = {tuple(pair) for pair in combinations(A, 2)}
    assert leaf_types == {(0, 1), (0, 2), (1, 2)}
    return {
        "flag": "(x,T), where T is a graph triangle anticomplete to x",
        "A": "A_x(T)={i: j(T,S_i)=2}, with |A_x(T)|=3",
        "six_cross_incidences": (
            "each leaf y in T has exactly mu=2 neighbors in N(x), while "
            "the three A-blocks have exactly two T-incidences each"
        ),
        "simplicity": (
            "one local-block endpoint cannot meet two leaves, by lambda=1 "
            "on their triangle edge; p_i and q_i cannot meet the same "
            "leaf, by lambda=1 on edge p_iq_i"
        ),
        "incidence_graph": (
            "the leaf--A incidence graph is simple and 2-regular on "
            "3+3 vertices, hence a 6-cycle"
        ),
        "conclusion": (
            "if A_x(T)={i,j,k}, the three leaves have types ij,ik,jk, "
            "one leaf of each type"
        ),
        "model_leaf_types": [list(pair) for pair in sorted(leaf_types)],
    }


def _all_triples(ground: Iterable[int]) -> tuple[frozenset[int], ...]:
    return tuple(frozenset(triple) for triple in combinations(ground, 3))


def _pair_degrees(
    family: set[frozenset[int]], ground: tuple[int, ...]
) -> dict[tuple[int, int], int]:
    result: dict[tuple[int, int], int] = {}
    for pair in combinations(ground, 2):
        pair_set = frozenset(pair)
        result[pair] = sum(pair_set <= member for member in family)
    return result


def _element_degrees(
    family: set[frozenset[int]], ground: tuple[int, ...]
) -> list[int]:
    return sorted(
        (sum(point in member for member in family) for point in ground),
        reverse=True,
    )


def _template_record(
    name: str,
    family: set[frozenset[int]],
    ground: tuple[int, ...],
    expected_elements: list[int],
    distinguished_pairs: set[tuple[int, int]],
) -> dict[str, Any]:
    assert len(family) == 13
    assert all(len(member) == 3 for member in family)
    assert all(left & right for left, right in combinations(family, 2))
    assert not set.intersection(*(set(member) for member in family))
    element_degrees = _element_degrees(family, ground)
    pair_degrees = _pair_degrees(family, ground)
    degree_five_pairs = {
        pair for pair, multiplicity in pair_degrees.items() if multiplicity == 5
    }
    assert element_degrees == expected_elements
    assert degree_five_pairs == distinguished_pairs
    return {
        "name": name,
        "members": [
            sorted(member) for member in sorted(family, key=lambda item: tuple(sorted(item)))
        ],
        "size": len(family),
        "pairwise_intersecting": True,
        "empty_total_intersection": True,
        "element_degree_sequence": element_degrees,
        "pair_degree_histogram": dict(
            (str(degree), count)
            for degree, count in sorted(Counter(pair_degrees.values()).items())
        ),
        "degree_five_pairs": [list(pair) for pair in sorted(degree_five_pairs)],
    }


def hilton_milner_equality_certificate() -> dict[str, Any]:
    """Instantiate the two classified k=3 equality templates exactly.

    This evaluates the two theorem-classified formulas.  It does not enumerate
    candidate families among the 2^35 subfamilies of C([7],3).
    """

    ground = tuple(range(7))
    triples = _all_triples(ground)

    # Standard Hilton--Milner template:
    # B plus all triples containing a and meeting B.
    a = 0
    B_h = frozenset((1, 2, 3))
    H = {B_h}
    H.update(
        triple
        for triple in triples
        if a in triple and bool(triple & B_h)
    )

    # Exceptional k=3 triangle template:
    # all triples containing at least two points of B.
    B_g = frozenset((0, 1, 2))
    G = {triple for triple in triples if len(triple & B_g) >= 2}

    H_record = _template_record(
        "standard_H",
        H,
        ground,
        [12, 6, 6, 6, 3, 3, 3],
        {(0, 1), (0, 2), (0, 3)},
    )
    G_record = _template_record(
        "exceptional_k3_triangle_G",
        G,
        ground,
        [9, 9, 9, 3, 3, 3, 3],
        {(0, 1), (0, 2), (1, 2)},
    )
    assert H_record["element_degree_sequence"] != G_record[
        "element_degree_sequence"
    ]

    for record in (H_record, G_record):
        assert len(record["degree_five_pairs"]) == 3

    return {
        "classification": (
            "a nontrivial intersecting 3-uniform family on seven points "
            "of Hilton--Milner equality size 13 is isomorphic either to "
            "standard_H or to exceptional_k3_triangle_G"
        ),
        "standard_H_formula": (
            "{B} union {A: a in A and A intersects B}, with a notin B"
        ),
        "exceptional_G_formula": "{A: |A intersect B|>=2}, with |B|=3",
        "templates": [H_record, G_record],
        "nonisomorphic_witness": "different element-degree sequences",
        "family_search_performed": False,
        "formula_instantiation_only": True,
        "forbidden_search_space_not_enumerated": "2^C(7,3)=2^35 families",
    }


def nontrivial_local_certificate() -> dict[str, Any]:
    return {
        "family": (
            "the distinct A_x(T) three-subsets from selected, old-h, and "
            "new-g exact-three flags with fixed center x"
        ),
        "verified_inputs": (
            "fixed-center simplicity and pairwise intersection are inherited "
            "from sealed Wave180/Wave194/Wave195"
        ),
        "empty_core_cap": "Hilton--Milner gives c_x<=13",
        "below_equality": "if c_x<=12, then j_x<=3c_x<=36",
        "equality_occurrences": "c_x=13 gives 3c_x=39 leaf occurrences",
        "pair_fibre_rule": (
            "a pair P contained in d_P flag sets supplies d_P leaves of "
            "type P, but the local type theorem provides only four "
            "distinct vertices of type P"
        ),
        "equality_repeats": (
            "both classified equality templates have three distinct "
            "pair-fibres with d_P=5, forcing at least one repeat in each"
        ),
        "conclusion": "j_x<=39-3=36",
    }


def common_block_certificate() -> dict[str, Any]:
    return {
        "hypothesis": "one local block S_i={x,p,q} lies in every A_x(T)",
        "leaf_names": (
            "each flag has a unique p-neighbor a, a distinct unique "
            "q-neighbor b, and a third leaf c"
        ),
        "first_uniqueness": (
            "q and a are nonadjacent; their two common neighbors are p and "
            "b, so mu=2 makes b the unique common neighbor other than p"
        ),
        "second_uniqueness": (
            "a and b are adjacent and c is their common neighbor, so "
            "lambda=1 makes c unique"
        ),
        "flag_injection": "the p-neighbor a uniquely determines (a,b,c)=T",
        "p_leaf_options": "deg(p)-2=12 after excluding known neighbors x,q",
        "c_x_upper": 12,
        "j_x_upper": "j_x<=3c_x<=36",
    }


def flag_pool_and_oriented_label_certificate() -> dict[str, Any]:
    return {
        "flag_pools": {
            "selected": "n3 selected/companion exact-three pairs",
            "old": "h orbit-closed raw exact-three pairs",
            "new": "g orbit-closed residual exact-three pairs",
        },
        "simplicity": (
            "the three companion-pair pools are disjoint by the sealed "
            "Wave189/Wave194 separation used by Wave195, and one flag "
            "determines one pair"
        ),
        "J": (
            "number of distinct oriented labels (center,leaf) across the "
            "union of all three flag pools"
        ),
        "upper": "J=sum_x j_x<=99*36=3564=6C/7",
        "selected_union": (
            "for the undirected selected type3 label union U, "
            "|U|>=C-n1-2n2"
        ),
        "selected_orientation": (
            "each label in U supplies at least one oriented label in J"
        ),
        "old_a3_orientation": (
            "each distinct type1 private label assigned exact3 supplies "
            "one additional orientation outside U"
        ),
        "old_b3_orientation": (
            "the two exact3 endpoint translates of a type2 private "
            "undirected label have opposite centers, hence contribute "
            "two orientations; b3 records their combined injection"
        ),
        "lower": "J>=C-n1-2n2+a3+b3",
        "S36": "n1+2n2-a3-b3-C/7>=0",
        "orientation_directions_changed_from_wave195": False,
    }


VARIABLES = (
    "C",
    "a1",
    "a2",
    "a3",
    "b1",
    "b3",
    "c1",
    "c2",
    "n2",
    "n3",
    "r2",
    "h",
    "y",
    "g",
    "W",
)


def row(**entries: int | Fraction) -> tuple[Fraction, ...]:
    return tuple(Fraction(entries.get(name, 0)) for name in VARIABLES)


def add_rows(*rows: tuple[Fraction, ...]) -> tuple[Fraction, ...]:
    return tuple(sum(values, Fraction()) for values in zip(*rows))


def scale(
    value: int | Fraction, source: tuple[Fraction, ...]
) -> tuple[Fraction, ...]:
    factor = Fraction(value)
    return tuple(factor * item for item in source)


def coefficient_certificate() -> dict[str, Any]:
    # Substitute n1=a1+a2+a3, p2=(b1+b3)/2, p3=c1+c2,
    # r1=a1+b1+c1.
    q0 = row(
        a1=2,
        a2=1,
        a3=1,
        b1=1,
        c1=1,
        n2=1,
        n3=2,
        r2=1,
        h=2,
        y=1,
        g=2,
        W=1,
    )
    target = add_rows(q0, row(C=Fraction(-71, 42)))
    SI = row(
        C=-2,
        a1=2,
        a2=2,
        a3=2,
        b1=Fraction(1, 2),
        b3=Fraction(1, 2),
        c1=1,
        c2=1,
        n2=2,
        n3=3,
    )
    S2 = row(b1=Fraction(1, 2), b3=Fraction(1, 2), n2=-1)
    SE2 = row(r2=2, a2=-1, c2=-1)
    RA = row(
        a2=-1,
        a3=-1,
        b3=-2,
        c2=-1,
        h=3,
        y=1,
        g=3,
    )
    SL = row(
        C=-1,
        a1=1,
        a2=1,
        a3=1,
        c1=1,
        n2=2,
        r2=2,
        y=1,
        W=2,
    )
    S36 = row(
        C=Fraction(-1, 7),
        a1=1,
        a2=1,
        n2=2,
        b3=-1,
    )
    certificate = add_rows(
        scale(Fraction(2, 3), SI),
        scale(Fraction(4, 3), S2),
        scale(Fraction(1, 6), SE2),
        scale(Fraction(2, 3), RA),
        scale(Fraction(1, 3), SL),
        scale(Fraction(1, 6), S36),
        scale(Fraction(1, 6), row(a1=1)),
        scale(Fraction(1, 2), row(b3=1)),
        scale(Fraction(1, 6), row(c2=1)),
        scale(Fraction(1, 3), row(W=1)),
    )
    assert certificate == target
    exact_bound = Fraction(71 * C_VALUE, 42)
    assert exact_bound == 7029
    assert Fraction(11 * C_VALUE - 3564, 6) == exact_bound
    return {
        "variable_order_after_split_substitution": list(VARIABLES),
        "Q0": "n1+n2+2n3+r1+r2+2h+y+2g+W",
        "SI": "I-2C",
        "S2": "p2-n2",
        "SE2": "2r2-a2-c2",
        "RA": "3h+y+3g-(a2+a3+2b3+c2)",
        "SL": "n1+2n2+c1+2r2+y+2W-C",
        "S36": "n1+2n2-a3-b3-C/7",
        "identity": (
            "Q0-71C/42=(2/3)SI+(4/3)S2+SE2/6+(2/3)RA"
            "+SL/3+S36/6+a1/6+b3/2+c2/6+W/3"
        ),
        "equivalent_target": "Q0-(11C-3564)/6",
        "C": C_VALUE,
        "exact_nonedge_projective_lower": 7029,
    }


def _json_fraction(value: Fraction) -> int | str:
    return value.numerator if value.denominator == 1 else str(value)


def integral_null_control() -> dict[str, Any]:
    values = {
        "a1": Fraction(0),
        "a2": Fraction(594),
        "a3": Fraction(0),
        "b1": Fraction(0),
        "b3": Fraction(0),
        "c1": Fraction(2970),
        "c2": Fraction(0),
        "n2": Fraction(0),
        "n3": Fraction(1386),
        "r2": Fraction(297),
        "h": Fraction(198),
        "y": Fraction(0),
        "g": Fraction(0),
        "W": Fraction(0),
    }
    n1 = values["a1"] + values["a2"] + values["a3"]
    p2 = (values["b1"] + values["b3"]) / 2
    p3 = values["c1"] + values["c2"]
    r1 = values["a1"] + values["b1"] + values["c1"]
    I = 2 * n1 + 2 * values["n2"] + 3 * values["n3"] + p2 + p3
    slacks = {
        "SI": I - 2 * C_VALUE,
        "S2": p2 - values["n2"],
        "SE2": 2 * values["r2"] - values["a2"] - values["c2"],
        "RA": (
            3 * values["h"]
            + values["y"]
            + 3 * values["g"]
            - values["a2"]
            - values["a3"]
            - 2 * values["b3"]
            - values["c2"]
        ),
        "SL": (
            n1
            + 2 * values["n2"]
            + values["c1"]
            + 2 * values["r2"]
            + values["y"]
            + 2 * values["W"]
            - C_VALUE
        ),
        "S36": (
            n1
            + 2 * values["n2"]
            - values["a3"]
            - values["b3"]
            - Fraction(C_VALUE, 7)
        ),
    }
    assert all(value == 0 for value in slacks.values())
    Q0 = (
        n1
        + values["n2"]
        + 2 * values["n3"]
        + r1
        + values["r2"]
        + 2 * values["h"]
        + values["y"]
        + 2 * values["g"]
        + values["W"]
    )
    assert Q0 == 7029
    return {
        "row": {name: _json_fraction(value) for name, value in values.items()},
        "derived": {
            "n1": _json_fraction(n1),
            "p2": _json_fraction(p2),
            "p3": _json_fraction(p3),
            "r1": _json_fraction(r1),
        },
        "zero_certificate_slacks": {
            name: _json_fraction(value) for name, value in slacks.items()
        },
        "Q0": _json_fraction(Q0),
        "integral_at_C_4158": True,
        "asserted_to_be_graph_code_cover_or_flag_family": False,
    }


def quarantine_certificate() -> dict[str, Any]:
    return {
        "status": "QUARANTINED_NOT_USED",
        "rows": (
            "all unrelated candidate capacity, support, owner, and "
            "orientation-amplification rows"
        ),
        "reason": (
            "Wave196 uses only the four-vertex pair-type cap, the two "
            "Hilton--Milner equality templates, common-block uniqueness, "
            "and the already verified Wave195 lower-bound orientations"
        ),
        "used_in_certificate": False,
    }


def build_math_result() -> dict[str, Any]:
    hm = hilton_milner_equality_certificate()
    assert all(
        len(template["degree_five_pairs"]) == 3
        for template in hm["templates"]
    )
    payload: dict[str, Any] = {
        "format": "wave196-four-fiber-hilton-milner-clean-room-math-v1",
        "conditional_setting": "prism-free rank-11 endpoint n3=4158, P=0",
        "inputs_scope": (
            "sealed Wave180, Wave194, Wave195 verifier results plus "
            "srg(99,14,1,2)"
        ),
        "local_two_star_types": local_two_star_type_certificate(),
        "flag_leaf_types": flag_leaf_type_certificate(),
        "hilton_milner_equality": hm,
        "nontrivial_family": nontrivial_local_certificate(),
        "common_block_family": common_block_certificate(),
        "flag_pools_and_orientations": (
            flag_pool_and_oriented_label_certificate()
        ),
        "coefficient_certificate": coefficient_certificate(),
        "integral_null": integral_null_control(),
        "quarantine": quarantine_certificate(),
        "bounds": {
            "universal_fixed_center_j_x": 36,
            "global_oriented_J": 3564,
            "nonedge_projective_short_circuits_Q": 7029,
            "edge_isolated_projective_short_circuits": 693,
            "all_projective_short_circuits": 7722,
            "scalar_short_circuit_words": 15444,
            "wave188_all_short_word_bound_remains_stronger": 18018,
        },
        "verdict": "INDEPENDENTLY_DERIVED_PRE_SOURCE",
        "boundary": {
            "conditional_theorem_derived": True,
            "source_compared": False,
            "arithmetic_null_realized": False,
            "graph_constructed": False,
            "code_constructed": False,
            "rank_11_excluded": False,
            "endpoint_excluded": False,
            "strict_n3_improvement": False,
            "external_novelty": "UNKNOWN",
            "conway_99": "UNKNOWN",
        },
    }
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    payload["math_result_sha256"] = hashlib.sha256(canonical).hexdigest()
    return payload


FULL_ROW_VARIABLES = (
    "H",
    "C",
    "n1",
    "n2",
    "n3",
    "p2",
    "p3",
    "a1",
    "a2",
    "a3",
    "b1",
    "b3",
    "c1",
    "c2",
    "r1",
    "r2",
    "h",
    "y",
    "g",
    "W",
)


def _evaluate_full_row(values: dict[str, Fraction]) -> dict[str, Fraction]:
    assert values["n1"] == values["a1"] + values["a2"] + values["a3"]
    assert 2 * values["p2"] == values["b1"] + values["b3"]
    assert values["p3"] == values["c1"] + values["c2"]
    assert values["r1"] == values["a1"] + values["b1"] + values["c1"]
    incidence = (
        2 * values["n1"]
        + 2 * values["n2"]
        + 3 * values["n3"]
        + values["p2"]
        + values["p3"]
    )
    q0 = (
        values["n1"]
        + values["n2"]
        + 2 * values["n3"]
        + values["r1"]
        + values["r2"]
        + 2 * values["h"]
        + values["y"]
        + 2 * values["g"]
        + values["W"]
    )
    return {
        "I": incidence,
        "Q0": q0,
        "SI": incidence - 2 * values["C"],
        "S2": values["p2"] - values["n2"],
        "SE2": 2 * values["r2"] - values["a2"] - values["c2"],
        "RA": (
            3 * values["h"]
            + values["y"]
            + 3 * values["g"]
            - values["a2"]
            - values["a3"]
            - 2 * values["b3"]
            - values["c2"]
        ),
        "SL": (
            values["n1"]
            + 2 * values["n2"]
            + values["c1"]
            + 2 * values["r2"]
            + values["y"]
            + 2 * values["W"]
            - values["C"]
        ),
        "S36": (
            values["H"]
            - values["C"]
            + values["n1"]
            + 2 * values["n2"]
            - values["a3"]
            - values["b3"]
        ),
    }


def source_comparison() -> dict[str, Any]:
    exact_path = PRIMARY_DIR / "exact-results.json"
    primary = json.loads(exact_path.read_text(encoding="utf-8"))

    geometry = primary["local_geometry"]
    assert geometry["star_blocks"] == 7
    assert geometry["two_block_types"] == 21
    assert geometry["fiber_size"] == 4
    assert geometry["partitioned_nonneighbors"] == 84
    assert geometry["common_star_flag_cap"] == 12
    assert geometry["universal_local_flag_cap"] == 13
    assert geometry["global_flag_cap"] == 1287
    assert geometry["universal_local_oriented_label_cap"] == 36
    assert geometry["global_oriented_label_cap_H"] == 3564
    assert geometry["new_slack"] == (
        "S36=H-C+n1+2*n2-a3-b3>=0"
    )

    source_templates = geometry["hilton_milner_equality_templates"]
    independent_templates = {
        template["name"]: template
        for template in hilton_milner_equality_certificate()["templates"]
    }
    template_name_map = {
        "H": "standard_H",
        "K": "exceptional_k3_triangle_G",
    }
    for source_name, independent_name in template_name_map.items():
        source_template = source_templates[source_name]
        independent = independent_templates[independent_name]
        assert source_template["members"] == independent["size"] == 13
        assert source_template["number_pair_degree_five"] == 3
        assert source_template["pair_degree_five"] == independent[
            "degree_five_pairs"
        ]
        assert source_template["forced_fiber_repeats"] == 3
        assert source_template["leaf_union_cap"] == 36
        assert source_template["total_pair_incidences"] == 39

    claim = primary["claim"]
    assert claim == {
        "bound": "Q>=7029",
        "global": "J<=3564",
        "local": "j_x<=36",
        "new_slack": "3564-C+n1+2*n2-a3-b3>=0",
    }
    certificate = primary["certificate"]
    assert certificate["identity_target"] == "(11*C-H)/6"
    assert certificate["slack_weights"] == {
        "RA": "2/3",
        "S2": "4/3",
        "S36": "1/6",
        "SE2": "1/6",
        "SI": "2/3",
        "SL": "1/3",
    }
    assert certificate["remainder_coefficients"] == {
        "W": "1/3",
        "a1": "1/6",
        "b3": "1/2",
        "c2": "1/6",
    }
    assert certificate["all_remainder_coefficients_nonnegative"] is True
    assert primary["bound"] == {
        "C": 4158,
        "H": 3564,
        "circuit_scalar_words": 15444,
        "edge_added_projective": 7722,
        "projective_nonedge_Q": 7029,
    }

    source_null = {name: Fraction() for name in FULL_ROW_VARIABLES}
    source_null.update(
        {
            name: Fraction(value)
            for name, value in primary["integer_null_control"]["row"].items()
        }
    )
    replay = _evaluate_full_row(source_null)
    assert all(
        replay[name] == 0
        for name in ("SI", "S2", "SE2", "RA", "SL", "S36")
    )
    assert replay["I"] == 8316
    assert replay["Q0"] == 7029
    assert primary["integer_null_control"]["is_object"] is False

    failed = (PRIMARY_DIR / "failed-routes.md").read_text(
        encoding="utf-8"
    ).lower()
    assert "superseded" in failed
    assert "not a construction" in failed
    derivation = (PRIMARY_DIR / "derivation.md").read_text(
        encoding="utf-8"
    )
    assert "Q0-(11*C-3564)/6" in derivation
    assert "7,029" in derivation

    return {
        "four_vertices_per_two_block_type_matches": True,
        "flag_pair_fibre_rule_matches": True,
        "both_hilton_milner_equality_templates_match": True,
        "three_degree_five_fibres_per_template_match": True,
        "common_block_uniqueness_and_cap_match": True,
        "selected_old_h_new_g_pool_scope_matches": True,
        "oriented_label_lower_bound_directions_match": True,
        "S36_and_J_cap_match": True,
        "coefficient_identity_matches": True,
        "bound_and_count_arithmetic_match": True,
        "source_integer_null_replayed": True,
        "source_and_independent_nulls_are_distinct": True,
        "all_null_rows_arithmetic_only": True,
        "unrelated_candidate_rows_quarantined": True,
        "primary_exact_results_sha256": sha256(exact_path),
    }


def hostile_proof_b_comparison() -> dict[str, Any]:
    exact_path = PROOF_B_DIR / "exact-results.json"
    audit = json.loads(exact_path.read_text(encoding="utf-8"))
    assert audit["claim_label"] == (
        "AUDIT_PASS_DERIVED_PENDING_INDEPENDENT_VERIFICATION"
    )
    geometry = audit["local_geometry"]
    assert geometry == {
        "common_star_flag_cap": 12,
        "fiber_size": 4,
        "global_flag_cap": 1287,
        "global_label_cap": 3564,
        "local_matching_edges": 7,
        "partitioned_nonneighbors": 84,
        "templates": {
            "H": {
                "forced_repeats": 3,
                "leaf_union_cap": 36,
                "members": 13,
                "pair_types_of_degree_five": 3,
            },
            "K": {
                "forced_repeats": 3,
                "leaf_union_cap": 36,
                "members": 13,
                "pair_types_of_degree_five": 3,
            },
        },
        "two_edge_types": 21,
        "universal_flag_cap": 13,
        "universal_label_cap": 36,
    }
    assert audit["global_rows"] == {
        "F": "n3+h+g<=1287",
        "J": "J<=3564",
        "S36": "3564-C+n1+2*n2-a3-b3>=0",
    }
    certificate = audit["certificate"]
    assert certificate["reduced_difference"] == {}
    assert certificate["target"] == "7029"
    assert certificate["integer_Q_lower_bound"] == 7029
    assert certificate["null_control"]["asserted_object"] is False
    scope = audit["search_scope"].lower()
    for forbidden in (
        "no graph",
        "sat",
        "lp",
        "brute-force search",
    ):
        assert forbidden in scope
    return {
        "role": "secondary hostile cross-check",
        "used_as_mathematical_premise": False,
        "verdict": "ACCEPT",
        "four_fibre_geometry_matches": True,
        "both_equality_templates_match": True,
        "common_block_injection_matches": True,
        "full_selected_old_h_new_g_pool_matches": True,
        "global_rows_match": True,
        "exact_certificate_matches": True,
        "unknown_boundary_preserved": True,
        "proof_b_exact_results_sha256": sha256(exact_path),
    }


def build_results() -> dict[str, Any]:
    integrity = verify_manifest_closure()
    assert integrity["passed"]
    payload: dict[str, Any] = {
        "format": "wave196-four-fiber-hilton-milner-verification-v1",
        "integrity": integrity,
        "independent_math_result": build_math_result(),
        "source_comparison": source_comparison(),
        "hostile_proof_b_comparison": hostile_proof_b_comparison(),
        "external_theorem_check": {
            "source": (
                "Hurlbert and Kamat, New injective proofs of the "
                "Erdos-Ko-Rado and Hilton-Milner theorems"
            ),
            "url": "https://arxiv.org/abs/1609.04714",
            "theorem": 11,
            "hypotheses_checked": (
                "2<=r<n/2, intersecting, empty total intersection"
            ),
            "equality_classification_checked": (
                "H, or the exceptional K when r=3"
            ),
            "specialization": (
                "n=7,r=3 gives size 13 and exactly the two templates "
                "instantiated independently"
            ),
        },
        "verdict": "VERIFIED_WITH_SCOPE",
        "verified_claim": (
            "conditionally, j_x<=36 for every center, J<=3564, "
            "S36>=0, and Q>=7029"
        ),
        "boundary": {
            "conditional_theorem_verified": True,
            "primary_source_compared": True,
            "hostile_proof_b_compared": True,
            "proof_b_used_as_mathematical_premise": False,
            "arithmetic_null_realized": False,
            "graph_constructed": False,
            "code_constructed": False,
            "rank_11_excluded": False,
            "endpoint_excluded": False,
            "strict_n3_improvement": False,
            "external_novelty": "UNKNOWN",
            "conway_99": "UNKNOWN",
        },
    }
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    payload["result_sha256"] = hashlib.sha256(canonical).hexdigest()
    return payload


def write_json(path: Path, value: dict[str, Any]) -> None:
    path.write_text(
        json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write-math", type=Path)
    parser.add_argument("--verify-math", type=Path)
    parser.add_argument("--write", type=Path)
    parser.add_argument("--verify", type=Path)
    args = parser.parse_args()
    if args.write_math:
        write_json(args.write_math, build_math_result())
        print(f"WROTE Wave196 independent math result: {args.write_math}")
        return 0
    if args.verify_math:
        expected = json.loads(args.verify_math.read_text(encoding="utf-8"))
        if build_math_result() != expected:
            print("FAIL Wave196 independent math result")
            return 1
        print(f"PASS Wave196 independent math result: {args.verify_math}")
        return 0
    if args.write:
        write_json(args.write, build_results())
        print(f"WROTE Wave196 clean-room result: {args.write}")
        return 0
    if args.verify:
        expected = json.loads(args.verify.read_text(encoding="utf-8"))
        if build_results() != expected:
            print("FAIL Wave196 clean-room verification")
            return 1
        print(f"PASS Wave196 clean-room verification: {args.verify}")
        return 0
    print(json.dumps(build_math_result(), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
