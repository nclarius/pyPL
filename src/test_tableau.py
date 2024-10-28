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
        assert len(tab) == 9

    def test_pl_validity(self):
        fml = Biimp(Neg(Conj(Prop("p"), Prop("q"))), Disj(Neg(Prop("p")), Neg(Prop("q"))))
        tab = Tableau(fml, propositional=True, silent=True)
        assert tab.closed()
        assert len(tab) == 19

    def test_pl_satisfiability(self):
        fml = Conj(Imp(Prop("p"), Prop("q")), Prop("r"))
        tab = Tableau(fml, validity=False, propositional=True, silent=True)
        assert tab.open()
        assert len(tab.models) == 2
        assert len(tab.models[1].v) == 2
        assert len(tab) == 5
    
    def test_fol_inf(self):
        fml1 = Exists(Var("y"), Forall(Var("x"), Atm(Pred("R"), (Var("x"), Var("y")))))
        fml2 = Forall(Var("x"), Exists(Var("y"), Atm(Pred("R"), (Var("x"), Var("y")))))
        tab = Tableau(fml2, premises=[fml1], silent=True)
        assert tab.closed()
        assert len(tab) == 7
        tab = Tableau(fml1, premises=[fml2], validity=True, silent=True)
        assert tab.infinite()
        assert len(tab) == 33
        tab = Tableau(fml1, premises=[fml2], validity=False, satisfiability=False, silent=True)
        assert tab.open()
        assert len(tab.models) > 0
        assert len(tab) == 12
    
    def test_fol_vadlidity(self):
        fml = Biimp(Forall(Var("x"), Atm(Pred("P"), (Var("x"),))),
                    Neg(Exists(Var("x"), Neg(Atm(Pred("P"), (Var("x"),))))))
        tab = Tableau(fml, silent=True)
        assert tab.closed()
        assert len(tab) == 13

        fml1 = Imp(Atm(Pred("P"), (Const("a"), Const("b"))),
                   Atm(Pred("Q"), (Const("a"), Const("c"))))
        fml = Atm(Pred("R"), (Const("a"), Const("a")))
        tab = Tableau(fml, premises=[fml1], silent=True)
        assert tab.open()
        assert len(tab.models) > 0
        assert len(tab) == 4

    def test_fol_satisfiability(self):
        fml = Conj(Exists(Var("x"), Atm(Pred("P"), (Var("x"),))),
                   Neg(Forall(Var("x"), Atm(Pred("P"), (Var("x"),)))))
        tab = Tableau(fml, validity=False, satisfiability=True, silent=True)
        assert tab.open()
        assert len(tab.models) > 0
        assert len(tab) == 7
    
        fml1 = Exists(Var("x"), Exists(Var("y"), Neg(Eq(Var("x"), Var("y")))))
        fml2 = Forall(Var("x"), Forall(Var("y"), Forall(Var("z"),
                      Disj(Eq(Var("x"), Var("y")), Eq(Var("x"), Var("z")), Eq(Var("y"), Var("z"))))))
        tab = Tableau(None, premises=[fml1, fml2], validity=False, silent=True)
        assert len(tab.models) == 1
        assert len(tab.models[0].d) == 2
        assert len(tab) == 72  # todo ineffficient
    
    def test_fol_eq(self):
        fml = Conj(Eq(Const("a"), Const("b")), Atm(Pred("P"), (Const("b"),)))
        tab = Tableau(fml, validity=False, satisfiability=True, silent=True)
        assert tab.open()
        assert len(tab) == 4
        assert len(tab.models) == 1
        assert len(tab.models[0].d) == 2
        
        fml = Exists(Var("x"), Conj(Eq(Var("x"), Const("b")), Atm(Pred("P"), (Var("x"),))))
        tab = Tableau(fml, validity=False, satisfiability=True, silent=True)
        assert tab.open()
        assert len(tab) == 4
        assert len(tab.models) == 1
        assert len(tab.models[0].d) == 1
    
    def test_ml_pl_validity(self):
        fml = Biimp(Nec(Prop("p")), Neg(Poss(Neg(Prop("p")))))
        tab = Tableau(fml, propositional=True, modal=True, silent=True)
        assert tab.closed()
        assert len(tab) == 13

    def test_ml_pl_satisfiability(self):
        fml1 = Nec(Disj(Prop("p"), Prop("q")))
        fml = Disj(Nec(Prop("p")), Nec(Prop("q")))
        tab = Tableau(fml, premises=[fml1], validity=False, satisfiability=False, propositional=True, modal=True, silent=True)
        assert tab.open()
        assert len(tab.models) > 0
        assert tab.models[0].v == {"p": {"w1": False, "w2": True}, "q": {"w1": True, "w2": False}}
        assert len(tab) == 14

    def test_ml_fol_validity(self):
        fml1 = Poss(Exists(Var("x"), Atm(Pred("P"), (Var("x"),))))
        fml = Exists(Var("x"), Poss(Atm(Pred("P"), (Var("x"),))))
        tab = Tableau(fml, premises=[fml1], modal=True, silent=True)
        assert tab.closed()
        assert len(tab) == 6

    def test_ml_fol_satisfiability(self):
        fml = Imp(Nec(Exists(Var("x"), Atm(Pred("P"), (Var("x"),)))),
                  Exists(Var("x"), Nec(Atm(Pred("P"), (Var("x"),)))))
        tab = Tableau(fml, modal=True, validity=False, satisfiability=False, silent=True)
        assert tab.open()
        assert len(tab.models) > 0
        assert tab.models[0].i == {"P": {"w1": {("a",)}, "w2": {("b",)}}}
        assert len(tab) == 13
    
    def test_ml_fol_domains(self):
        fml = Imp(Exists(Var("x"), Forall(Var("y"), Nec(Atm(Pred("Q"), (Var("x"), Var("y")))))),
                  Forall(Var("y"), Nec(Exists(Var("x"), Atm(Pred("Q"), (Var("x"), (Var("y"))))))))
        tab = Tableau(fml, modal=True, silent=True)
        assert tab.closed()
        assert len(tab) == 12
        tab = Tableau(fml, modal=True, vardomains=True, silent=True)
        assert tab.infinite()
        assert len(tab) == 39
        tab = Tableau(fml, validity=False, modal=True, vardomains=True, silent=True)
        assert tab.open()
        assert len(tab) == 7
        tab = Tableau(fml, validity=False, satisfiability=False, modal=True, vardomains=True, silent=True)
        assert tab.open()
        assert len(tab) == 12
    
    def test_il_pl(self):
        fml = Disj(Prop("p"), Neg(Prop("p")))
        tab = Tableau(fml, propositional=True, classical=False, silent=True)
        assert tab.infinite()
        assert len(tab) == 9
        tab = Tableau(fml, propositional=True, classical=False, validity=False, silent=True)
        assert tab.open()
        assert len(tab.models) == 2
        assert len(tab) == 3
        fml2 = Imp(Imp(Prop("p"), Prop("q")), Disj(Neg(Prop("p")), Prop("q")))
        tab = Tableau(fml2, propositional=True, classical=False, validity=False, satisfiability=False, silent=True)
        assert tab.open()
        assert len(tab.models) == 1
        assert len(tab) == 10
    
    def test_il_fol(self):
        fml1 = Neg(Forall(Var("x"), Neg(Atm(Pred("P"), (Var("x"),)))))
        fml = Exists(Var("x"), Atm(Pred("P"), (Var("x"),)))
        tab = Tableau(fml, premises=[fml1], classical=False, silent=True)
        assert tab.infinite()
        assert len(tab) == 25
    
    def test_strategy(self):
        fml1 = Neg(Forall(Var("x"), Exists(Var("y"), Atm(Pred("P"), (Var("x"), Var("y"))))))
        fml = Exists(Var("x"), Forall(Var("y"), Neg(Atm(Pred("P"), (Var("x"), Var("y"))))))
        tab = Tableau(fml, premises=[fml1], silent=True)
        assert tab.closed()
        assert len(tab) == 9

        fml = Conj(Exists(Var("x"), Atm(Pred("P"), (Var("x"),))),
                   Forall(Var("x"), Neg(Atm(Pred("P"), (Var("x"),)))))
        tab = Tableau(fml, validity=False, satisfiability=True, silent=True)
        assert tab.closed()
        assert len(tab) == 9

if __name__ == '__main__':
    unittest.main()
