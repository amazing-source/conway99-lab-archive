import importlib.util
import pathlib
import unittest


HERE = pathlib.Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("wave127_jacobi_lp", HERE / "jacobi_lp.py")
MODEL = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODEL)


class ExactJacobiModelTests(unittest.TestCase):
    def test_character(self):
        self.assertEqual(
            [MODEL.chi(n) for n in range(7)],
            [0, 1, 1, -1, 1, -1, -1],
        )

    def test_a_normalization(self):
        aa = MODEL.phi_minus2(1)
        self.assertEqual(
            [aa.get((0, r), 0) for r in (-1, 0, 1)],
            [1, -2, 1],
        )

    def test_b_normalization(self):
        bb = MODEL.phi_zero(1)
        self.assertEqual(
            [bb.get((0, r), 0) for r in (-1, 0, 1)],
            [1, 10, 1],
        )

    def test_a_is_even_in_z(self):
        aa = MODEL.phi_minus2(2)
        self.assertTrue(all(aa.get((n, -r), 0) == value for (n, r), value in aa.items()))

    def test_b_is_even_in_z(self):
        bb = MODEL.phi_zero(2)
        self.assertTrue(all(bb.get((n, -r), 0) == value for (n, r), value in bb.items()))

    def test_dimensions(self):
        dimensions = [
            MODEL.modular_dimension(22 + 2 * c)
            for c in range(11)
        ]
        self.assertEqual(
            dimensions,
            [15, 17, 17, 19, 21, 21, 23, 25, 25, 27, 29],
        )
        self.assertEqual(sum(dimensions), 239)

    def test_exact_sturm_rank_at_each_weight(self):
        for c in range(11):
            weight = 22 + 2 * c
            basis = MODEL.modular_basis(weight, 2)
            self.assertEqual(len(basis), MODEL.modular_dimension(weight))

    def test_product_fricke_is_an_involution(self):
        for product in (
            ((3, "C"), (19, "C")),
            ((3, "C"), (19, "T")),
            ((3, "T"), (19, "C")),
            ((3, "T"), (19, "T")),
        ):
            factor = MODEL.Q(-1)
            mapped = []
            for weight, orientation in product:
                exponent = (
                    (weight - 1) // 2
                    if orientation == "C"
                    else (1 - weight) // 2
                )
                factor *= (
                    MODEL.Q(7**exponent)
                    if exponent >= 0
                    else MODEL.Q(1, 7 ** (-exponent))
                )
                mapped.append(
                    (weight, "T" if orientation == "C" else "C")
                )
            second = MODEL.Q(-1)
            for weight, orientation in mapped:
                exponent = (
                    (weight - 1) // 2
                    if orientation == "C"
                    else (1 - weight) // 2
                )
                second *= (
                    MODEL.Q(7**exponent)
                    if exponent >= 0
                    else MODEL.Q(1, 7 ** (-exponent))
                )
            self.assertEqual(factor * second, 1)


if __name__ == "__main__":
    unittest.main()
