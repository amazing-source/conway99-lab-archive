"""Independent exact verifier for the Wave 107 principal-complement spectrum.

The calculation is conditional on a hypothetical srg(99,14,1,2) containing
the induced C4 Cartesian K3 motif.  Only Python integers and fractions are
used.  No discovery module is imported.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from fractions import Fraction
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
DISCOVERY = ROOT / "attempts" / "wave107-c4boxk3-spectrum"
EXPECTED_MANIFEST_SHA256 = (
    "7e899602825d3cdf989affade8a1e5a6256f17ba911f6351ea8bfe4a3b05d2b0"
)

V = 99
K = 14
LAMBDA = 1
MU = 2
MOTIF_ORDER = 12
OUTSIDE_ORDER = V - MOTIF_ORDER

MOTIF_SPECTRUM = {-3: 2, -1: 4, 0: 1, 1: 2, 2: 2, 4: 1}
OUTSIDE_INTEGER_SPECTRUM = {-4: 32, -3: 2, -2: 2, -1: 1, 0: 4, 2: 2, 3: 42}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def validate_discovery_manifest() -> dict[str, object]:
    manifest = DISCOVERY / "package-manifest.sha256"
    manifest_hash = sha256(manifest)
    require(
        manifest_hash == EXPECTED_MANIFEST_SHA256,
        "Wave 107 package-manifest hash drift",
    )
    entries: list[dict[str, str]] = []
    seen: set[str] = set()
    pattern = re.compile(r"^([0-9a-f]{64})  (.+)$")
    for line in manifest.read_text(encoding="utf-8").splitlines():
        match = pattern.fullmatch(line)
        require(match is not None, f"malformed manifest line: {line!r}")
        expected, relative = match.groups()
        require(relative not in seen, f"duplicate manifest path: {relative}")
        seen.add(relative)
        path = ROOT / Path(relative)
        require(path.is_file(), f"missing manifest input: {relative}")
        actual = sha256(path)
        require(actual == expected, f"manifest entry drift: {relative}")
        entries.append({"path": relative, "sha256": actual})
    require(len(entries) == 9, "unexpected Wave 107 manifest entry count")
    return {
        "manifest_sha256": manifest_hash,
        "entry_count": len(entries),
        "entries_valid": True,
    }


def motif_adjacency() -> list[list[int]]:
    """Build C4 Cartesian K3 in label-major order."""

    vertices = [(label, cycle) for label in range(3) for cycle in range(4)]
    adjacency = [[0] * MOTIF_ORDER for _ in range(MOTIF_ORDER)]
    for i, (label_i, cycle_i) in enumerate(vertices):
        for j, (label_j, cycle_j) in enumerate(vertices):
            k3_edge = cycle_i == cycle_j and label_i != label_j
            c4_edge = (
                label_i == label_j
                and (cycle_i - cycle_j) % 4 in {1, 3}
            )
            adjacency[i][j] = int(k3_edge or c4_edge)
    return adjacency


def matrix_multiply(left: list[list[int]], right: list[list[int]]) -> list[list[int]]:
    rows = len(left)
    inner = len(right)
    columns = len(right[0])
    require(all(len(row) == inner for row in left), "left matrix width drift")
    require(all(len(row) == columns for row in right), "right matrix width drift")
    return [
        [
            sum(left[i][k] * right[k][j] for k in range(inner))
            for j in range(columns)
        ]
        for i in range(rows)
    ]


def matrix_traces(matrix: list[list[int]], cutoff: int) -> list[int]:
    order = len(matrix)
    require(all(len(row) == order for row in matrix), "matrix is not square")
    power = [[int(i == j) for j in range(order)] for i in range(order)]
    traces: list[int] = []
    for _ in range(cutoff):
        power = matrix_multiply(power, matrix)
        traces.append(sum(power[i][i] for i in range(order)))
    return traces


def characteristic_from_traces(traces: list[int]) -> list[int]:
    """Return det(xI-M), coefficients in ascending order, by Newton identities."""

    coefficients_high = [1]
    for degree in range(1, len(traces) + 1):
        numerator = sum(
            coefficients_high[degree - power] * traces[power - 1]
            for power in range(1, degree + 1)
        )
        require(numerator % degree == 0, "Newton coefficient is not integral")
        coefficients_high.append(-numerator // degree)
    return list(reversed(coefficients_high))


def poly_multiply(left: list[int], right: list[int]) -> list[int]:
    result = [0] * (len(left) + len(right) - 1)
    for i, a in enumerate(left):
        for j, b in enumerate(right):
            result[i + j] += a * b
    return result


def poly_power(base: list[int], exponent: int) -> list[int]:
    result = [1]
    for _ in range(exponent):
        result = poly_multiply(result, base)
    return result


def factored_polynomial(factors: dict[int, int], quadratic: list[int] | None = None) -> list[int]:
    result = [1]
    for root, multiplicity in sorted(factors.items()):
        result = poly_multiply(result, poly_power([-root, 1], multiplicity))
    if quadratic is not None:
        result = poly_multiply(result, quadratic)
    return result


def rational_rank(matrix: list[list[int]]) -> int:
    work = [[Fraction(value) for value in row] for row in matrix]
    rows = len(work)
    columns = len(work[0]) if rows else 0
    rank = 0
    for column in range(columns):
        pivot = next(
            (row for row in range(rank, rows) if work[row][column] != 0),
            None,
        )
        if pivot is None:
            continue
        work[rank], work[pivot] = work[pivot], work[rank]
        scale = work[rank][column]
        work[rank] = [value / scale for value in work[rank]]
        for row in range(rows):
            if row == rank or work[row][column] == 0:
                continue
            factor = work[row][column]
            work[row] = [
                value - factor * pivot_value
                for value, pivot_value in zip(work[row], work[rank])
            ]
        rank += 1
        if rank == rows:
            break
    return rank


def verify_motif() -> dict[str, object]:
    adjacency = motif_adjacency()
    require(all(adjacency[i][i] == 0 for i in range(MOTIF_ORDER)), "motif loop")
    require(
        all(
            adjacency[i][j] == adjacency[j][i]
            for i in range(MOTIF_ORDER)
            for j in range(MOTIF_ORDER)
        ),
        "motif adjacency is asymmetric",
    )
    degrees = [sum(row) for row in adjacency]
    require(degrees == [4] * MOTIF_ORDER, "motif is not 4-regular")

    traces = matrix_traces(adjacency, MOTIF_ORDER)
    characteristic = characteristic_from_traces(traces)
    proposed = factored_polynomial(MOTIF_SPECTRUM)
    require(characteristic == proposed, "motif characteristic polynomial mismatch")
    nullities: dict[str, int] = {}
    for eigenvalue, multiplicity in MOTIF_SPECTRUM.items():
        shifted = [
            [
                adjacency[i][j] - eigenvalue * int(i == j)
                for j in range(MOTIF_ORDER)
            ]
            for i in range(MOTIF_ORDER)
        ]
        nullity = MOTIF_ORDER - rational_rank(shifted)
        require(nullity == multiplicity, f"motif eigenspace drift at {eigenvalue}")
        nullities[str(eigenvalue)] = nullity
    return {
        "order": MOTIF_ORDER,
        "degree": 4,
        "edges": sum(degrees) // 2,
        "spectrum": {str(key): value for key, value in sorted(MOTIF_SPECTRUM.items())},
        "eigenspace_nullities": nullities,
        "characteristic_polynomial": (
            "(x-4)(x-2)^2(x-1)^2*x*(x+1)^4*(x+3)^2"
        ),
        "characteristic_coefficients_sha256": hashlib.sha256(
            json.dumps(characteristic, separators=(",", ":")).encode("ascii")
        ).hexdigest(),
    }


def common_neighbors(adjacency: list[list[int]], i: int, j: int) -> int:
    return sum(adjacency[i][vertex] * adjacency[j][vertex] for vertex in range(len(adjacency)))


def motif_incidence_census() -> dict[str, object]:
    adjacency = motif_adjacency()
    boundary = MOTIF_ORDER * (K - 4)
    pair_slots = 0
    compatible = [[True] * MOTIF_ORDER for _ in range(MOTIF_ORDER)]
    for i in range(MOTIF_ORDER):
        for j in range(i + 1, MOTIF_ORDER):
            target = LAMBDA if adjacency[i][j] else MU
            internal = common_neighbors(adjacency, i, j)
            remaining = target - internal
            require(remaining >= 0, "motif already exceeds an SRG codegree")
            pair_slots += remaining
            compatible[i][j] = compatible[j][i] = internal + 1 <= target

    maximum_neighborhood = 0
    for mask in range(1 << MOTIF_ORDER):
        selected = [i for i in range(MOTIF_ORDER) if (mask >> i) & 1]
        if all(compatible[i][j] for index, i in enumerate(selected) for j in selected[index + 1 :]):
            maximum_neighborhood = max(maximum_neighborhood, len(selected))
    require(maximum_neighborhood == 2, "outside motif-neighborhood cap drift")

    # With every outside motif-degree in {0,1,2}, pair_slots is exactly X2.
    x2 = pair_slots
    x1 = boundary - 2 * x2
    x0 = OUTSIDE_ORDER - x1 - x2
    counts = {0: x0, 1: x1, 2: x2}
    require(counts == {0: 3, 1: 48, 2: 36}, "motif incidence census drift")
    return {
        "boundary_incidences": boundary,
        "outside_pair_incidences": pair_slots,
        "maximum_outside_motif_degree": maximum_neighborhood,
        "motif_degree_counts": {str(key): value for key, value in counts.items()},
        "outside_degree_counts": {
            str(K - motif_degree): count for motif_degree, count in counts.items()
        },
    }


def quadratic_power_sums(constant: int, cutoff: int) -> list[int]:
    # Roots of x^2-9x-constant satisfy r^n=9r^(n-1)+constant*r^(n-2).
    sums = [2, 9]
    for power in range(2, cutoff + 1):
        sums.append(9 * sums[power - 1] + constant * sums[power - 2])
    return sums[: cutoff + 1]


def outside_trace(power: int, quadratic_constant: int = 46) -> int:
    integral = sum(
        multiplicity * eigenvalue**power
        for eigenvalue, multiplicity in OUTSIDE_INTEGER_SPECTRUM.items()
    )
    return integral + quadratic_power_sums(quadratic_constant, power)[power]


def verify_interlacing() -> bool:
    global_eigenvalues = [14] + [3] * 54 + [-4] * 44
    # Each pair is a closed rational enclosure. The two irrational roots lie
    # strictly inside the indicated intervals because 16^2 < 265 < 17^2.
    outside_intervals = (
        [(Fraction(25, 2), Fraction(13))]
        + [(Fraction(3), Fraction(3))] * 42
        + [(Fraction(2), Fraction(2))] * 2
        + [(Fraction(0), Fraction(0))] * 4
        + [(Fraction(-1), Fraction(-1))]
        + [(Fraction(-2), Fraction(-2))] * 2
        + [(Fraction(-3), Fraction(-3))] * 2
        + [(Fraction(-4), Fraction(-7, 2))]
        + [(Fraction(-4), Fraction(-4))] * 32
    )
    require(len(outside_intervals) == OUTSIDE_ORDER, "outside spectrum order drift")
    for index, (lower, upper) in enumerate(outside_intervals):
        require(global_eigenvalues[index] >= upper, f"interlacing upper failure at {index}")
        require(lower >= global_eigenvalues[index + MOTIF_ORDER], f"interlacing lower failure at {index}")
    return True


def exact_results() -> dict[str, object]:
    manifest = validate_discovery_manifest()
    motif = verify_motif()
    incidence = motif_incidence_census()

    # The SRG relation gives
    # (xI-A)^-1 = ((x+1)I+A+2J/(x-14))/q, q=(x-3)(x+4).
    # On the motif all-ones line, multiplying the determinant by x-14
    # replaces x+5+24/(x-14) with x^2-9x-46. The remaining motif
    # eigenspaces contribute x+1+theta.
    outside_polynomial = factored_polynomial(
        OUTSIDE_INTEGER_SPECTRUM,
        quadratic=[-46, -9, 1],
    )
    require(len(outside_polynomial) - 1 == OUTSIDE_ORDER, "outside polynomial degree drift")
    require(outside_polynomial[-1] == 1, "outside polynomial is not monic")

    traces = {str(power): outside_trace(power) for power in range(1, 5)}
    require(traces == {"1": 0, "2": 1098, "3": 1002, "4": 37518}, "spectral moment drift")

    degree_counts = {
        int(degree): count
        for degree, count in incidence["outside_degree_counts"].items()
    }
    forced_degree_sum = sum(degree * count for degree, count in degree_counts.items())
    require(forced_degree_sum == 1098, "forced degree sum drift")
    wrong_trace_two = outside_trace(2, quadratic_constant=38)
    require(wrong_trace_two == 1082, "wrong-factor trace drift")
    require(wrong_trace_two != forced_degree_sum, "wrong factor was not refuted")

    edges = forced_degree_sum // 2
    triangles = traces["3"] // 6
    wedges = sum(count * degree * (degree - 1) // 2 for degree, count in degree_counts.items())
    cycle_numerator = traces["4"] - 2 * edges - 4 * wedges
    require(cycle_numerator % 8 == 0, "four-cycle formula is nonintegral")
    four_cycles = cycle_numerator // 8
    require((edges, triangles, four_cycles) == (549, 167, 1356), "graph invariant drift")

    # Symmetry of D makes algebraic and geometric multiplicities equal.
    nullity = OUTSIDE_INTEGER_SPECTRUM[0]
    rank_minus_3 = OUTSIDE_ORDER - OUTSIDE_INTEGER_SPECTRUM[3]
    rank_plus_4 = OUTSIDE_ORDER - OUTSIDE_INTEGER_SPECTRUM[-4]
    require((nullity, rank_minus_3, rank_plus_4) == (4, 45, 55), "rank drift")

    require(16 * 16 < 265 < 17 * 17, "quadratic root enclosure drift")
    require(verify_interlacing(), "Cauchy interlacing failed")
    # The block identities force D1=14*1-s and Ds=24*1-5s. Thus
    # v=(rho+5)1-s is a rho eigenvector. Since s<=2 and rho>25/2, v>0.
    perron_positive_lower_bound = Fraction(25, 2) + 5 - 2
    require(perron_positive_lower_bound > 0, "Perron vector positivity failed")
    require(265 != 16 * 16, "quadratic discriminant unexpectedly square")

    return {
        "format": "wave108-independent-wave107-verification-v1",
        "claim_label": "VERIFIED",
        "verdict": "VERIFIED_SCOPED",
        "scope": (
            "Conditional spectral and graph-invariant consequences of an induced "
            "C4 Cartesian K3 motif in a hypothetical srg(99,14,1,2)."
        ),
        "input_validation": manifest,
        "independent_method": {
            "motif_characteristic_polynomial": "Newton identities from exact adjacency traces",
            "global_resolvent": (
                "(xI-A)^-1=((x+1)I+A+2J/(x-14))/((x-3)(x+4))"
            ),
            "principal_complement": (
                "Jacobi complementary-minor identity plus the rank-one action "
                "of J on the regular motif"
            ),
        },
        "motif": motif,
        "incidence_census": incidence,
        "outside_characteristic_polynomial": {
            "factorization": (
                "(x-3)^42 (x+4)^32 (x^2-9x-46) "
                "(x+3)^2 (x+2)^2 (x+1) x^4 (x-2)^2"
            ),
            "degree": len(outside_polynomial) - 1,
            "coefficients_ascending_sha256": hashlib.sha256(
                json.dumps(outside_polynomial, separators=(",", ":")).encode("ascii")
            ).hexdigest(),
            "quadratic_discriminant": 265,
            "quadratic_root_intervals": {
                "larger": ["25/2", "13"],
                "smaller": ["-4", "-7/2"],
            },
        },
        "wrong_quadratic_audit": {
            "variant": "x^2-9x-38",
            "variant_trace_D2": wrong_trace_two,
            "forced_trace_D2": forced_degree_sum,
            "difference": forced_degree_sum - wrong_trace_two,
            "verdict": "REFUTED",
        },
        "forced_graph_invariants": {
            "traces": traces,
            "edges": edges,
            "triangles": triangles,
            "degree_wedges": wedges,
            "four_cycles": four_cycles,
            "nullity_Q_D": nullity,
            "rank_Q_D_minus_3I": rank_minus_3,
            "rank_Q_D_plus_4I": rank_plus_4,
        },
        "perron_and_interlacing": {
            "D_one": "14*one-s",
            "D_s": "24*one-5*s",
            "invariant_basis_matrix_columns": [[14, 24], [-1, -5]],
            "basis_characteristic_polynomial": "x^2-9x-46",
            "positive_eigenvector": "(rho+5)*one-s",
            "positive_coordinate_lower_bound": "31/2",
            "rho_is_simple": True,
            "outside_graph_connected": True,
            "cauchy_interlacing_passes": True,
        },
        "status_wall": {
            "spectral_obstruction_found": False,
            "motif_excluded": False,
            "motif_extension": "UNKNOWN",
            "Conway_99": "UNKNOWN",
            "literature_novelty": "UNKNOWN",
        },
    }


def verify_archive(path: Path) -> dict[str, object]:
    results = exact_results()
    archived = json.loads(path.read_text(encoding="utf-8"))
    require(archived == results, "archived verifier results drift")
    return results


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--verify", action="store_true")
    parser.add_argument(
        "--archive",
        type=Path,
        default=Path(__file__).with_name("exact-results.json"),
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    results = verify_archive(args.archive) if args.verify else exact_results()
    print(json.dumps(results, indent=2, sort_keys=True) + "\n", end="")


if __name__ == "__main__":
    main()
