import unittest

from expr import *
from tableau import *


class TestTableau(unittest.TestCase):

    def test_pl_inf(self):
        fml1 = Imp(Prop("p"), Prop("q"))
        fml2 = Imp(Prop("q"), Prop("r"))
        fml = Imp(Prop("p"), Prop("r"))
        tab = Tableau(fml, premises=[fml1, fml2], propositional=True, silent=True)
        assert tab.closed()

    def test_pl_validity(self):
        fml = Biimp(Neg(Conj(Prop("p"), Prop("q"))), Disj(Neg(Prop("p")), Neg(Prop("q"))))
        tab = Tableau(fml, propositional=True, silent=True)
        assert tab.closed()

    def test_pl_satisfiability(self):
        fml = Conj(Imp(Prop("p"), Prop("q")), Prop("r"))
        tab = Tableau(fml, validity=True, propositional=True, silent=True)
        assert tab.open()
        assert len(tab.models) == 2
        assert len(tab.models[1].v) == 2
    
    def test_fol_inf(self):
        fml1 = Exists(Var("y"), Forall(Var("x"), Atm(Pred("R"), (Var("x"), Var("y")))))
        fml2 = Forall(Var("x"), Exists(Var("y"), Atm(Pred("R"), (Var("x"), Var("y")))))
        tab = Tableau(fml2, premises=[fml1], silent=True)
        assert tab.closed()
        tab = Tableau(fml1, premises=[fml2], validity=True, silent=True)
        assert tab.infinite()
        tab = Tableau(fml1, premises=[fml2], validity=False, satisfiability=False, silent=True)
        assert tab.open()
        assert len(tab.models) > 0
    
    def test_fol_vadlidity(self):
        fml = Biimp(Forall(Var("x"), Atm(Pred("P"), (Var("x"),))),
                    Neg(Exists(Var("x"), Neg(Atm(Pred("P"), (Var("x"),))))))
        tab = Tableau(fml, silent=True)
        assert tab.closed()

        fml1 = Imp(Atm(Pred("P"), (Const("a"), Const("b"))),
                   Atm(Pred("Q"), (Const("a"), Const("c"))))
        fml = Atm(Pred("R"), (Const("a"), Const("a")))
        tab = Tableau(fml, premises=[fml1], silent=True)
        assert tab.open()
        assert len(tab.models) > 0

    def test_fol_satisfiability(self):
        fml = Conj(Exists(Var("x"), Atm(Pred("P"), (Var("x"),))),
                   Neg(Forall(Var("x"), Atm(Pred("P"), (Var("x"),)))))
        tab = Tableau(fml, validity=False, satisfiability=True, silent=True)
        assert tab.open()
        assert len(tab.models) > 0
    
        fml1 = Forall(Var("x"), Forall(Var("y"), Forall(Var("z"),
                      Disj(Disj(Eq(Var("x"), Var("y")), Eq(Var("x"), Var("z"))), Eq(Var("y"), Var("z"))))))
        fml2 = Exists(Var("x"), Exists(Var("y"), Neg(Eq(Var("x"), Var("y")))))
        tab = Tableau(None, premises=[fml1, fml2], validity=False, hide_nonopen=True, silent=True)
        assert len(tab.models) == 1
        assert len(tab.models[0].d) == 2
    
    def test_ml_pl_validity(self):
        fml = Biimp(Nec(Prop("p")), Neg(Poss(Neg(Prop("p")))))
        tab = Tableau(fml, propositional=True, modal=True, silent=True)
        assert tab.closed()

    def test_ml_pl_satisfiability(self):
        fml1 = Nec(Disj(Prop("p"), Prop("q")))
        fml = Disj(Nec(Prop("p")), Nec(Prop("q")))
        tab = Tableau(fml, premises=[fml1], validity=False, satisfiability=False, propositional=True, modal=True, silent=True)
        assert tab.open()
        assert len(tab.models) > 0
        assert tab.models[0].v == {"p": {"w1": False, "w2": True}, "q": {"w1": True, "w2": False}}

    def test_ml_fol_validity(self):
        fml1 = Poss(Exists(Var("x"), Atm(Pred("P"), (Var("x"),))))
        fml = Exists(Var("x"), Poss(Atm(Pred("P"), (Var("x"),))))
        tab = Tableau(fml, premises=[fml1], modal=True, silent=True)
        assert tab.closed()

    def test_ml_fol_satisfiability(self):
        fml = Imp(Nec(Exists(Var("x"), Atm(Pred("P"), (Var("x"),)))),
                  Exists(Var("x"), Nec(Atm(Pred("P"), (Var("x"),)))))
        tab = Tableau(fml, modal=True, validity=False, satisfiability=False, silent=True)
        assert tab.open()
        assert len(tab.models) > 0
        assert tab.models[0].i == {"P": {"w1": {("a",)}, "w2": {("b",)}}}
    
    def test_ml_fol_domains(self):
        fml = Imp(Exists(Var("x"), Forall(Var("y"), Nec(Atm(Pred("Q"), (Var("x"), Var("y")))))),
                  Forall(Var("y"), Nec(Exists(Var("x"), Atm(Pred("Q"), (Var("x"), (Var("y"))))))))
        tab = Tableau(fml, modal=True, silent=True)
        assert tab.closed()
        tab = Tableau(fml, modal=True, vardomains=True, silent=True)
        assert tab.infinite()
        tab = Tableau(fml, validity=False, modal=True, vardomains=True, silent=True)
        assert tab.open()
        tab = Tableau(fml, validity=False, satisfiability=False, modal=True, vardomains=True, silent=True)
        assert tab.open()
    
    def test_il_pl(self):
        fml = Disj(Prop("p"), Neg(Prop("p")))
        tab = Tableau(fml, propositional=True, classical=False, silent=True)
        assert tab.infinite()
        tab = Tableau(fml, propositional=True, classical=False, validity=False, silent=True)
        assert tab.open()
        assert len(tab.models) == 2
    
    def test_il_fol(self):
        fml1 = Neg(Forall(Var("x"), Neg(Atm(Pred("P"), (Var("x"),)))))
        fml = Exists(Var("x"), Atm(Pred("P"), (Var("x"),)))
        tab = Tableau(fml, premises=[fml1], classical=False, silent=True)
        assert tab.infinite()
    
    def test_strategy(self):
        fml1 = Neg(Forall(Var("x"), Exists(Var("y"), Atm(Pred("P"), (Var("x"), Var("y"))))))
        fml = Exists(Var("x"), Forall(Var("y"), Neg(Atm(Pred("P"), (Var("x"), Var("y"))))))
        tab = Tableau(fml, premises=[fml1], silent=True)
        assert tab.closed()
        assert len(tab) == 9

if __name__ == '__main__':
    unittest.main()