import unittest

from expr import *


class TestExpr(unittest.TestCase):
    def test_props(self):
        fml = Exists(Var("x"), Conj(Atm(Pred("P"), (Var("x"),)), Atm(Pred("R"), (Var("x"), Var("y"), Const("c")))))
        assert len(fml) == 11
        assert fml.freevars() == {"y"}
        assert fml.boundvars() == {"x"}
        assert fml.consts() == {"c"}

    def test_normalforms(self):
        fml = Imp(Disj(Prop("p"), Prop("q")), Neg(Prop("r")))
        dnf = Disj(Conj(Prop("p"), Prop("q"), Neg(Prop("r"))),
                  Conj(Prop("p"), Neg(Prop("q")), Neg(Prop("r"))),
                  Conj(Neg(Prop("p")), Prop("q"), Neg(Prop("r"))),
                  Conj(Neg(Prop("p")), Neg(Prop("q")), Prop("r")),
                  Conj(Neg(Prop("p")), Neg(Prop("q")), Neg(Prop("r"))))
        assert str(fml.dnf()) == str(dnf)
        cnf = Conj(Disj(Neg(Prop("p")), Neg(Prop("q")), Neg(Prop("r"))),
                   Disj(Neg(Prop("p")), Prop("q"), Neg(Prop("r"))),
                   Disj(Prop("p"), Neg(Prop("q")), Neg(Prop("r"))))
        assert str(fml.cnf()) == str(cnf)
        assert fml.clauses() == [[(False, "p"), (False, "q"), (False, "r")],
                                 [(False, "p"), (True, "q"), (False, "r")],
                                 [(True, "p"), (False, "q"), (False, "r")]]
        
        fml = Exists(Var("x"), Atm(Pred("P"), (Var("x"), Var("y"), Var("z"))))
        assert fml.univ_closure() == Forall(Var("y"), Forall(Var("z"), Exists(Var("x"), Atm(Pred("P"), (Var("x"), Var("y"), Var("z"))))))
    
    def test_constr_arglens(self):
        fml = Conj()
        assert fml == Verum()
        fml = Conj(Prop("p"))
        assert fml == Prop("p")
        fml = Conj(Prop("p"), Prop("q"))
        assert fml == Conj(Prop("p"), Prop("q"))
        fml = Conj(Prop("p"), Prop("q"), Prop("r"), Prop("s"))
        assert fml == Conj(Prop("p"), Conj(Prop("q"), Conj(Prop("r"), Prop("s"))))


if __name__ == '__main__':
    unittest.main()
