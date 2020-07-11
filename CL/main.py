#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Main module. Input specification and program execution are defined here."""
from functools import reduce

from expr import *
from structure import *
# from tableau import *


# settings
denots = [8, 9, 10]  # set here which denotations to include in the output (see def.s in fnc. 'compute_denots')
tableaus = [1, 2] # set here which tableaus to include in the output (see def.s in fnc. 'compute_denots')
verbose = True  # set this to True if you'd like intermediate steps to be printed out, and False otherwise


def compute_denots():
    """
    Define structures and formulas to compute denotations for here.
    """
    global depth, active


    if 1 in active:
        ############################
        print("\n---------------------------------\n")
        ############################

        print("Example #1: tupperware boxes, lids and a bunny (logic for linguists lecture 010)")
        print()

        d1 = {"roundbox", "roundlid", "rectbox", "rectlid", "bunny"}
        i1 = {"b1": "roundbox", "b2": "rectbox", "f": "bunny",
              "box": {("roundbox", ), ("rectbox", )},
              "lid": {("roundlid", ), ("rectlid", )},
              "fit": {("roundlid", "roundbox"), ("rectlid", "rectbox")}
        }
        m1 = PredStructure("M1", d1, i1)
        v1 = {"x": "roundbox", "y": "bunny"}
        vv1 = {"x": "bunny", "y": "rectbox"}

        print(m1)
        print("v1 = " + str(v1))
        print("v'1 = " + str(vv1))

        e1 = {
            1: Var("x"),
            2: Const("f"),
            3: Atm(Pred("box"), (Var("x"), )),
            4: Forall(Var("x"), Imp(Atm(Pred("box"), (Var("x"), )),
                                    Exists(Var("y"), Conj(Atm(Pred("lid"), (Var("y"), )),
                                                          Atm(Pred("fit"), (Var("y"), Var("x"))))))),
            5: Exists(Var("y"), Conj(Atm(Pred("lid"), (Var("y"), )),
                                     Forall(Var("x"), Imp(Atm(Pred("box"), (Var("x"), )),
                                                          Atm(Pred("fit"), (Var("y"), Var("x")))))))
        }

        for nr, e in e1.items():
            if nr <= 3:
                print()
                print("⟦" + str(e) + "⟧^M1,v1 =")
                print(e.denot(m1, v1))
                depth = 0
                print()
                print("⟦" + str(e) + "⟧^M1,v'1 =")
                print(e.denot(m1, vv1))
                depth = 0
            if nr > 3:
                print()
                print("⟦" + str(e) + "⟧^M1 =")
                print(e.denotV(m1))
                depth = 0


    if 2 in active:
        #############################
        print("\n---------------------------------\n")
        ############################

        print("Example #2: MMiL (logic for linguists Example #from the book)")
        print()

        d2 = {"Mary", "Jane", "MMiL"}
        i2 = {"m": "Mary",
              "student": {("Mary", ), ("Jane", )},
              "book": {("MMiL", )},
              "read": {("Mary", "MMiL")}
        }
        m2 = PredStructure("D2", d2, i2)
        v2 = {"x": "Jane", "y": "Mary", "z": "MMiL"}

        print(m2)
        print("v = " + str(v2))

        e2 = {
            1: Var("x"),  # Jane
            2: Const("m"),  # Mary
            3: Pred("read"),  # {(Mary, MMiL)}
            4: Atm(Pred("book"), (Var("x"), )),  # false, since Jane is not a book
            5: Exists(Var("x"), Conj(Atm(Pred("book"), (Var("x"),)), Atm(Pred("read"), (Const("m"), Var("x"))))), # true
            6: Forall(Var("y"), Imp(Atm(Pred("student"), (Var("y"), )),
                                    Exists(Var("x"),
                                           Conj(Atm(Pred("book"), (Var("x"), )),
                                                Atm(Pred("read"), (Var("y"), Var("z"))))))),
               # false, since Jane doesn't read a book
            7: Neg(Exists(Var("y"), Conj(Atm(Pred("student"), (Var("y"), )),
                                         Exists(Var("x"),
                                                Conj(Atm(Pred("book"), (Var("x"), )),
                                                     Atm(Pred("read"), (Var("y"), (Var("z")))))))))
               # false, since Mary reads a book
        }

        for nr, e in e2.items():
            print()
            print("⟦" + str(e) + "⟧^M2,v2 =")
            print(e.denot(m2, v2))
            depth = 0


    if 3 in active:
        #############################
        print("\n---------------------------------\n")
        #############################

        print("Example #3: love #1 (logic for linguists ExSh 10 Ex. 1)")
        print()

        d3 = {"Mary", "John", "Peter"}
        i3 = {"j": "Peter", "p": "John",
              "woman": {("Mary",)},
              "man": {("John", ), ("Peter", )},
              "love": {("Mary", "John"), ("John", "Mary"), ("John", "John"), ("Peter", "Mary"), ("Peter", "John")},
              "jealous": {("Peter", "John", "Mary"), ("Peter", "Mary", "John")}}
        m3 = PredStructure("M3", d3, i3)
        v3 = {"x": "Mary", "y": "Mary", "z": "Peter"}
        vv3 = {"x": "John", "y": "Peter", "z": "John"}

        print(m3)
        print("v = " + str(v3))
        print("v' = " + str(vv3))

        e3 = {
            1: Const("p"),
            2: Var("y"),
            3: Var("y"),
            4: Atm(Pred("love"), (Const("p"), Const("j"))),
            5: Atm(Pred("love"), (Var("y"), Var("z"))),
            6: Atm(Pred("love"), (Var("y"), Var("z"))),
            7: Exists(Var("x"), Neg(Atm(Pred("love"), (Const("j"), Var("x"))))),
            8: Forall(Var("x"), Exists(Var("y"), Atm(Pred("love"), (Var("x"), Var("y"))))),
            9: Neg(Forall(Var("x"), Imp(Atm(Pred("woman"), (Var("x"),)),
                                         Exists(Var("y"), Conj(Atm(Pred("man"), (Var("y"),)),
                                                               Atm(Pred("love"), (Var("x"), Var("y"))))
                                                )))),
            10: Neg(Exists(Var("y"), Exists(Var("z"), Atm(Pred("jealous"), (Const("j"), Var("y"), Var("z"))))))
        }

        for nr, e in e3.items():
            # print(e)
            if nr in [1, 2, 4, 5, 7, 8, 9]:
                print()
                print("⟦" + str(e) + "⟧^M3,v3 =")
                print(e.denot(m3, v3))
                depth = 0
            elif nr in [3, 6, 10]:
                print()
                print("⟦" + str(e) + "⟧^M3,v'3 =")
                print(e.denot(m3, vv3))
                depth = 0


    if 4 in active:
        #############################
        print("\n---------------------------------\n")
        #############################

        print("(Example #4: love #2 (modification of Example #3)")
        print()

        d4 = {"Mary", "John", "Susan"}
        i4 = {"m": "Mary", "j": "John", "s": "Susan",
              "rain": {},
              "sun": {()},
              "woman": {("Mary",), ("Susan",)}, "man": {("John",)},
              "love": {("John", "Mary"), ("Mary", "Susan"), ("Susan", "Mary"), ("Susan", "Susan")},
              "jealous": {("John", "Susan", "Mary")}}
        m4 = PredStructure("M4", d4, i4)
        v4 = m4.vs[5]

        print(m4)
        print("v = " + str(v4))

        e4 = {
            1: Var("x"),  # Susan
            2: Const("j"),  # John
            3: Pred("love"),  # {(J,M), (M,S), (S,M), (S,S)}
            4: Atm(Pred("love"), (Var("x"), Const("m"))),  # true under g, false in m
            5: Atm(Pred("love"), (Const("j"), Const("m"))),  # true
            6: Exists(Var("x"), Atm(Pred("love"), (Const("j"), Var("x")))),  # true
            7: Forall(Var("x"), Atm(Pred("love"), (Const("j"), Var("x")))),  # false
            8: Conj(Atm(Pred("love"), (Const("m"), Const("s"))), Atm(Pred("love"), (Const("s"), Const("m")))),  # true
            9: Forall(Var("x"), Imp(Atm(Pred("love"), (Const("s"), Var("x"))), Atm(Pred("woman"), (Var("x"),)))),# true
            10: Neg(Exists(Var("x"), Atm(Pred("love"), (Var("x"), Var("x"))))),  # false
            11: Neg(Forall(Var("x"), Atm(Pred("love"), (Var("x"), Var("x"))))),  # true
            12: Forall(Var("x"), Imp(Atm(Pred("woman"), (Var("x"),)),
                                     Exists(Var("y"), Conj(Atm(Pred("man"), (Var("y"),)),
                                                           Atm(Pred("love"), (Var("x"), Var("y"))))))),  # false
            13: Imp(
                Conj(Conj(Atm(Pred("love"), (Var("x"), Var("y"))),
                          Atm(Pred("love"), (Var("y"), Var("z")))),
                     Neg(Atm(Pred("love"), (Var("y"), Var("x"))))),
                Atm(Pred("jealous"), (Var("x"), Var("z"), Var("y")))),  # true
            14: Conj(Exists(Var("x"), Atm(Pred("love"), (Var("x"), Var("x")))), Atm(Pred("woman"), (Var("x"),))),
            15: Atm(Pred("rain"), ()),
            16: Atm(Pred("sun"), ())
        }

        for nr, e in e4.items():
            if 1 <= nr <= 4:
                print()
                print("⟦" + str(e) + "⟧^M4,v4 =")
                print(e.denot(m4, v4))
                depth = 0
            if 4 <= nr <= 16:
                print()
                print("⟦" + str(e) + "⟧^M4 =")
                print(e.denotV(m4))
                depth = 0
            # if nr == 14:
            #     print(e.freevars())
            #     print(e.boundvars())


    if 5 in active:
        #############################
        print("\n---------------------------------\n")
        #############################

        print("Example #5: term equality and function symbols")
        print()

        d5 = {"Mary", "Peter", "Susan", "Jane"}
        i5 = {"m": "Mary", "s": "Susan", "j": "Jane",
              "mother": {("Mary",): "Susan", ("Peter",): "Susan", ("Susan",): "Jane"}}
        m5 = PredStructure("M5", d5, i5)
        v5 = {"x": "Susan", "y": "Mary", "z": "Peter"}

        print(m5)
        print("v = " + str(v5))

        e5 = {
            1: FuncTerm(Func("mother"), (Const("m"),)),  # Susan
            2: FuncTerm(Func("mother"), (FuncTerm(Func("mother"), (Const("m"),)),)),  # Jane
            3: Eq(FuncTerm(Func("mother"), (Const("m"),)), Const("s")),  # true
            4: Neg(Eq(Var("x"), Const("m")))  # true
        }

        for nr, e in e5.items():
            print()
            print("⟦" + str(e) + "⟧^M5,v5 =")
            print(e.denot(m5, v5))
            depth = 0


    if 6 in active:
        #############################
        print("\n---------------------------------\n")
        #############################

        print("Example #6: modal logic with constant domain")
        print()

        w6 = {"w1", "w2"}
        r6 = {("w1", "w1"), ("w1", "w2"), ("w2", "w2"), ("w2", "w2")}
        d6 = {"a"}
        i6 = {"w1": {"P": {()}},
              "w2": {"P": set()}}
        m6 = ConstModalStructure("M6", w6, r6, d6, i6)
        v6 = m6.vs[0]

        print(m6)
        print(v6)

        e6 = {
            1: Poss(Nec(Eq(Var("x"), Var("x")))),
            2: Nec(Disj(Atm(Pred("P"), tuple()), Neg(Atm(Pred("P"), tuple())))),
            3: Disj(Nec(Atm(Pred("P"), tuple())), Nec(Neg(Atm(Pred("P"), tuple()))))
        }

        for nr, e in e6.items():
            # print()
            # print("⟦" + str(e) + "⟧^M6,v6,w1 =")
            # print(e.denot(m6, v6, "w1"))
            # depth = 0
            # print()
            # print("⟦" + str(e) + "⟧^M6,v6,w2 =")
            # print(e.denot(m6, v6, "w2"))
            # depth = 0
            print("⟦" + str(e) + "⟧^M6,v6 =")
            print(e.denotW(m6, v6))
            depth = 0


    if 7 in active:
        #############################
        print("\n---------------------------------\n")
        #############################

        print("Example #7: modal logic with varying domain")
        print()

        w7 = {"w1", "w2"}
        r7 = {("w1", "w1"), ("w1", "w2"), ("w2", "w2"), ("w2", "w2")}
        d7 = {"w1": {"a"},
              "w2": {"a", "b"}}
        i7 = {"w1": {"P": {("a",)}},
              "w2": {"P": {("b",)}}}
        m7 = VarModalStructure("M7", w7, r7, d7, i7)

        print(m7)
        print(m7.vs)

        e7 = {
            1: Exists(Var("x"), Exists(Var("y"), Neg(Eq(Var("x"), Var("y")))))
        }

        for nr, e in e7.items():
            print()
            print("⟦" + str(e) + "⟧^M7,w1 =")
            print(e.denot(m7, m7.vs["w1"][0], "w1"))
            depth = 0
            print()
            print("⟦" + str(e) + "⟧^M7,w2 =")
            print(e.denot(m7, m7.vs["w2"][0], "w2"))
            depth = 0
            # print(e.denotV(m7))
            # print(e.denotW(m7, v7))
            # print(e.denotVW(m7))
            # depth = 0

    if 8 in active:
        #############################
        print("\n---------------------------------\n")
        #############################

        print("Example #8: propositional logic")
        print()

        v8a = {"p": True, "q": False, "r": True}
        m8a = PropStructure("M8", v8a)

        print(m8a)

        e8 = {
            1: Disj(Imp(Prop("p"), Prop("r")), Imp(Prop("q"), Prop("r")))
        }

        for nr, e in e8.items():
            print()
            print("⟦" + str(e) + "⟧^M9 =")
            print(e.denot(m8a))
            depth = 0

        v8b = {"p": True, "q": True, "r": False}
        m8b = PropStructure("M8'", v8b)

        print()

        print(m8b)

        for nr, e in e8.items():
            print()
            print("⟦" + str(e) + "⟧^M8' =")
            print(e.denot(m8b))
            depth = 0

    if 9 in active:
        #############################
        print("\n---------------------------------\n")
        #############################

        print("Example #9: predicate logic (logic for computer scientists lecture 07)")
        print()

        d9a = {"m1", "m2"}
        i9a = {"S": {("m1", )},
               "R": {("m1", "m1"), ("m2", "m1")}
              }
        m9a = PredStructure("M9a", d9a, i9a)

        print(m9a)

        e9 = {
            1: Forall(Var("x"), Exists(Var("y"),
                                       Conj(Atm(Pred("S"), (Var("y"), )), Atm(Pred("R"), (Var("x"), Var("y"))))))
        }

        for nr, e in e9.items():
            print()
            print("⟦" + str(e) + "⟧^M9 =")
            print(e.denotV(m9a))
            depth = 0

        print()

        d9b = {"m1", "m2"}
        i9b = {"S": {("m2", )},
               "R": {("m1", "m1"), ("m2", "m1")}
              }
        m9b = PredStructure("M9'", d9b, i9b)

        print(m9b)

        for nr, e in e9.items():
            print()
            print("⟦" + str(e) + "⟧^M9' =")
            print(e.denotV(m9b))
            depth = 0

    if 10 in active:
        #############################
        print("\n---------------------------------\n")
        #############################

        print("Example #10: predicate logic (logic for computer scientists exercise sheet 07)")
        print()

        d10 = {"a", "b", "c"}
        i10 = {"P": {("a",)},
               "R": {("a", "a"), ("a", "b"), ("a", "c"), ("b", "c")},
               "k": "b",
               "l": "a"
              }
        m10 = PredStructure("M10", d10, i10)

        print(m10)

        e10 = {
            1: Neg(Atm(Pred("R"), (Const("l"), Var("x")))),
            2: Exists(Var("x"), Exists(Var("y"), Atm(Pred("R"), (Var("x"), Var("y"))))),
            3: Forall(Var("x"), Exists(Var("y"),
                                       Conj(Atm(Pred("P"), (Var("x"),)), Atm(Pred("R"), (Var("x"), Var("y"))))))
        }

        for nr, e in e10.items():
            print()
            print("⟦" + str(e) + "⟧^M10 =")
            print(e.denotV(m10))
            depth = 0

        print()

    #############################
    print("\n---------------------------------\n")
    #############################


def compute_tableaus():

    if 1 in tableaus:
        fml1 = Conj(Imp(Prop("p"), Prop("q")), Prop("r"))
        tab1 = Tableau(fml1)
        tab1.generate()

    if 2 in tableaus:
        fml2 = Biimp(Neg(Conj(Prop("p"), Prop("q"))), Disj(Neg(Prop("p")), Neg(Prop("q"))))
        tab2 = Tableau(Neg(fml2))
        tab2.generate()


if __name__ == "__main__":
    compute_denots()
    # compute_tableaus()
