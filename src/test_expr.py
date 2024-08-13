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
        
        fml = Exists(Var("x"), Atm(Pred("P"), (Var("x"), Var("y"), Var("z"))))
        assert fml.univ_closure() == Forall(Var("y"), Forall(Var("z"), Exists(Var("x"), Atm(Pred("P"), (Var("x"), Var("y"), Var("z"))))))
    
    def test_edgeconstrs(self):
        fml = Conj()
        assert fml == Verum()
        fml = Conj(Prop("p"))
        assert fml == Prop("p")


if __name__ == '__main__':
    unittest.main()
