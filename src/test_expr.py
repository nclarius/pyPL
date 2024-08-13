import unittest

from expr import *


class TestExpr(unittest.TestCase):
    def test_normalforms(self):
        fml = Imp(Disj(Prop("p"), Prop("q")), Neg(Prop("r")))
        assert str(fml.cnf()) == "((¬p ∨ (¬q ∨ ¬r)) ∧ ((¬p ∨ (q ∨ ¬r)) ∨ (p ∨ (¬q ∨ ¬r))))"
        assert str(fml.dnf()) == "((p ∧ (q ∨ ¬r)) ∨ ((p ∧ (¬q ∨ ¬r)) ∨ ((¬p ∧ (q ∨ ¬r)) ∨ ((¬p ∧ (¬q ∨ r)) ∨ (¬p ∧ (¬q ∨ ¬r))))))"
        assert fml.clauses() == [[(False, "p"), (False, "q"), (False, "r")],
                                 [(False, "p"), (True, "q"), (False, "r")],
                                 [(True, "p"), (False, "q"), (False, "r")]]


if __name__ == '__main__':
    unittest.main()
