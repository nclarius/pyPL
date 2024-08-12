import unittest

from expr import *
from denotation import *


class TestDenotation(unittest.TestCase):
    def test_pl(self):
        v = {"p": True, "q": False, "r": True}
        s = PropStructure("S", v)
        e = Disj(Imp(Prop("p"), Prop("r")), Imp(Prop("q"), Prop("r")))
        assert e.denot(s) == True

    def test_fol(self):
        d = {"s1", "s1"}
        i = {"S": {("s1", )},
               "R": {("s1", "s1"), ("s1", "s1")}}
        s = PredStructure("S", d, i)
        e = Forall(Var("x"), Exists(Var("y"), Conj(Atm(Pred("S"), (Var("y"),)), Atm(Pred("R"), (Var("x"), Var("y"))))))
        assert e.denot(s) == True

        d = {"roundbox", "roundlid", "rectbox", "rectlid", "bunny"}
        i = {"b1": "roundbox", "b2": "rectbox", "f": "bunny",
              "box": {("roundbox", ), ("rectbox", )},
              "lid": {("roundlid", ), ("rectlid", )},
              "fit": {("roundlid", "roundbox"), ("rectlid", "rectbox")}
        }
        s = PredStructure("S", d, i)
        v = {"x": "roundbox", "y": "bunny"}
        e = Var("x")
        assert e.denot(s, v) == "roundbox"
        e = Const("f")
        assert e.denot(s) == "bunny"
        e = Atm(Pred("box"), (Var("x"),))
        assert e.denot(s, v) == True
        e = Forall(Var("x"), Imp(Atm(Pred("box"), (Var("x"),)), Exists(Var("y"), Conj(Atm(Pred("lid"), (Var("y"),)), Atm(Pred("fit"), (Var("y"), Var("x")))))))
        assert e.denot(s) == True
        e = Exists(Var("y"), Conj(Atm(Pred("lid"), (Var("y"),)), Forall(Var("x"), Imp(Atm(Pred("box"), (Var("x"),)), Atm(Pred("fit"), (Var("y"), Var("x")))))))
        assert e.denot(s) == False

        d = {"Mary", "Peter", "Susan", "Jane"}
        i = {"m": "Mary", "s": "Susan", "j": "Jane",
              "mother": {("Mary",): "Susan", ("Peter",): "Susan", ("Susan",): "Jane"}}
        s = PredStructure("S", d, i)
        e = Eq(FuncTerm(Func("mother"), (Const("m"),)), Const("s"))
        assert e.denot(s) == True
    
    def test_ml_pl(self):
        w = {"w1", "w2"}
        r = {("w1", "w2")}
        v = {"p": {"w1": False, "w2": True}}
        s = PropModalStructure("S", w, r, v)
        e = Imp(Nec(Prop("p")), Prop("p"))
        assert e.denotV(s, "w1") == False
        assert e.denotV(s, "w2") == True
        assert e.denotVW(s) == False
    
    def test_ml_fol_constdom(self):
        w = {"w1", "w2", "w3"}
        r = {("w1", "w2"), ("w1", "w3")}
        d = {"a", "b"}
        i = {"P": {"w1": set(), "w2": {("a",)}, "w3": {("b",)}}}
        s = ConstModalStructure("S", w, r, d, i)
        e = Imp(Forall(Var("x"), Poss(Atm(Pred("P"), (Var("x"),)))),
                Poss(Forall(Var("x"), Atm(Pred("P"), (Var("x"),)))))
        assert e.denotV(s, "w1") == False
        assert e.denotV(s, "w2") == True
        assert e.denotVW(s) == False
    
    def test_ml_fol_vardom(self):
        w = {"w1", "w2"}
        r = {("w1", "w2")}
        d = {"w1": {"a"}, "w2": {"a", "b"}}
        i = {"P": {"w1": set(), "w2": {("b",)}}}
        s = VarModalStructure("S", w, r, d, i)
        e = Imp(Poss(Exists(Var("x"), Atm(Pred("P"), (Var("x"),)))),
                Exists(Var("x"), Poss(Atm(Pred("P"), (Var("x"),)))))
        assert e.denotV(s, "w1") == False
        assert e.denotV(s, "w2") == True
        assert e.denotVW(s) == False
    
    def test_ml_intl(self):
        w = {"w0", "w1"}
        r = set()
        d = {"M", "JB", "DT"}
        i = {"mary": {"w0": "M", "w1": "M"},
             "biden": {"w0": "JB", "w1": "JB"},
             "trump": {"w0": "DT", "w1": "DT"},
             "president": {"w0": "JB", "w1": "DT"},
             "Democrat": {"w0": {("JB",)}, "w1": {("JB",)}},
             "Republican": {"w0": {("DT",)}, "w1": {("DT",)}},
             "Believe": {"w0": {("M", frozenset({("w0", True), ("w1", True)}))}, "w1": {("M", frozenset({("w0", True), ("w1", True)}))}}}

        s = ConstModalStructure("S", w, r, d, i)
        e = Const("president")
        assert e.denotV(s, "w0") == "JB"
        e = Int(Const("president"))
        assert e.denotV(s, "w0") == frozenset({("w0", "JB"), ("w1", "DT")})
        e = Ext(Int(Const("president")))
        assert e.denotV(s, "w0") == "JB"
        e = Atm(Pred("Democrat"), (Const("president"),))
        assert e.denotV(s, "w0") == True
        assert e.denotV(s, "w1") == False
        e = Atm(Pred("Believe"), (Const("mary"), Int(Atm(Pred("Democrat"), (Const("biden"),)))))
        assert e.denotV(s, "w0") == True
        e = Atm(Pred("Believe"), (Const("mary"), Int(Atm(Pred("Democrat"), (Const("president"),)))))
        assert e.denotV(s, "w0") == False

    def test_il(self):
        k = {"k0", "k1"}
        r = {("k0", "k1")}
        v = {"p": {"k0": False, "k1": True}}
        s = KripkePropStructure("S", k, r, v)
        e = Disj(Prop("p"), Neg(Prop("p")))
        assert e.denotVW(s) == False
        e = Neg(Neg(e))
        assert e.denotVW(s) == True

if __name__ == '__main__':
    unittest.main()
